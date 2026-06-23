from __future__ import annotations

import re
from functools import lru_cache

from pypinyin import Style, lazy_pinyin, pinyin
from pypinyin.pinyin_dict import pinyin_dict

from lyrics_converter.homophone.data import BLOCKED_CHARS, BLOCKED_WORDS, COMMON_CHARS, MANUAL_CANDIDATES, STROKES
from lyrics_converter.homophone.types import Candidate, HomophoneOptions, Pronunciation, ReplaceItem, ReplaceResult, ReplaceStats

PINYIN_KEY_RE = re.compile(r"^([a-züv]+)([0-5])$", re.IGNORECASE)
FREQUENCY_RANK = {char: index + 1 for index, char in enumerate(dict.fromkeys(COMMON_CHARS))}


def replace_homophones(text: str, options: HomophoneOptions | None = None) -> ReplaceResult:
    options = options or HomophoneOptions()
    output_chars: list[str] = []
    items: list[ReplaceItem] = []
    stats = ReplaceStats()
    recent_chars: dict[str, int] = {}

    for index, char in enumerate(text):
        if not is_chinese(char):
            output_chars.append(char)
            items.append(ReplaceItem(index, char, char, "", False, "non_chinese"))
            stats.non_chinese += 1
            continue

        stats.total_chinese += 1
        pronunciation = get_pronunciation(char)
        if not pronunciation.key:
            output_chars.append(char)
            items.append(ReplaceItem(index, char, char, "", False, "no_pronunciation"))
            stats.kept_original += 1
            continue

        candidates = get_candidates(pronunciation)
        filtered = filter_candidates(candidates, pronunciation, char, options)
        ranked = rank_candidates(filtered, recent_chars)
        selected = ranked[0] if ranked else None

        if selected:
            output_chars.append(selected.char)
            items.append(
                ReplaceItem(
                    index=index,
                    origin=char,
                    replacement=selected.char,
                    pinyin=pronunciation.key,
                    changed=True,
                    reason="replaced",
                    candidates=[candidate.char for candidate in ranked[:8]],
                )
            )
            stats.replaced += 1
            recent_chars[selected.char] = index
        else:
            output_chars.append(char)
            items.append(
                ReplaceItem(
                    index=index,
                    origin=char,
                    replacement=char,
                    pinyin=pronunciation.key,
                    changed=False,
                    reason="kept_original" if options.allow_original else "no_candidate",
                    candidates=[candidate.char for candidate in candidates[:8]],
                )
            )
            stats.kept_original += 1

    stats.blocked_fallbacks = fix_blocked_words(output_chars, items, BLOCKED_WORDS)
    if stats.blocked_fallbacks:
        stats.replaced = sum(1 for item in items if item.changed)
        stats.kept_original = stats.total_chinese - stats.replaced

    return ReplaceResult(text, "".join(output_chars), items, stats)


def is_chinese(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def parse_pinyin_key(key: str) -> tuple[str, int]:
    normalized = key.lower().replace("v", "ü")
    match = PINYIN_KEY_RE.match(normalized)
    if not match:
        return normalized, 0
    return match.group(1), int(match.group(2))


@lru_cache(maxsize=8192)
def get_pronunciation(char: str) -> Pronunciation:
    values = lazy_pinyin(char, style=Style.TONE3, neutral_tone_with_five=True, errors="ignore")
    key = values[0].lower().replace("v", "ü") if values else ""
    plain, tone = parse_pinyin_key(key)
    return Pronunciation(char=char, key=key, plain=plain, tone=tone)


@lru_cache(maxsize=8192)
def get_all_pinyin_keys(char: str) -> tuple[str, ...]:
    readings = pinyin(
        char,
        style=Style.TONE3,
        heteronym=True,
        neutral_tone_with_five=True,
        errors="ignore",
    )
    if not readings:
        return ()
    return tuple(sorted({item.lower().replace("v", "ü") for item in readings[0]}))


def is_polyphonic(char: str) -> bool:
    return len(get_all_pinyin_keys(char)) > 1


@lru_cache(maxsize=1)
def build_candidate_chars() -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for char in COMMON_CHARS:
        if char not in seen:
            seen.add(char)
            result.append(char)
    for codepoint in pinyin_dict:
        char = chr(codepoint)
        if char not in seen:
            seen.add(char)
            result.append(char)
    return tuple(result)


@lru_cache(maxsize=1)
def build_candidate_map() -> dict[str, list[Candidate]]:
    result: dict[str, list[Candidate]] = {}
    for key, chars in MANUAL_CANDIDATES.items():
        for char in chars:
            candidate = make_candidate(char, source="manual")
            if candidate:
                result.setdefault(key, []).append(candidate)

    for char in build_candidate_chars():
        candidate = make_candidate(char, source="auto")
        if candidate:
            result.setdefault(candidate.key, []).append(candidate)
    return result


def make_candidate(char: str, source: str) -> Candidate | None:
    pronunciation = get_pronunciation(char)
    if not pronunciation.key:
        return None
    return Candidate(
        char=char,
        key=pronunciation.key,
        plain=pronunciation.plain,
        tone=pronunciation.tone,
        stroke_count=STROKES.get(char),
        is_polyphonic=is_polyphonic(char),
        source=source,
    )


def get_candidates(target: Pronunciation) -> list[Candidate]:
    seen: set[str] = set()
    candidates: list[Candidate] = []
    for candidate in build_candidate_map().get(target.key, []):
        if candidate.char in seen:
            continue
        seen.add(candidate.char)
        candidates.append(candidate)
    return candidates


def filter_candidates(
    candidates: list[Candidate],
    target: Pronunciation,
    origin_char: str,
    options: HomophoneOptions,
) -> list[Candidate]:
    filtered: list[Candidate] = []
    for candidate in candidates:
        if candidate.char == origin_char:
            continue
        if candidate.char in BLOCKED_CHARS:
            continue
        if options.strict_tone and candidate.key != target.key:
            continue
        if not options.strict_tone and candidate.plain != target.plain:
            continue
        if options.avoid_polyphonic and candidate.is_polyphonic:
            continue
        if options.avoid_complex_chars:
            if candidate.stroke_count is None or candidate.stroke_count > options.max_strokes:
                continue
        filtered.append(candidate)
    return filtered


def rank_candidates(candidates: list[Candidate], recent_chars: dict[str, int]) -> list[Candidate]:
    scored: list[Candidate] = []
    for candidate in candidates:
        rank = FREQUENCY_RANK.get(candidate.char, 9999)
        stroke = candidate.stroke_count or 16
        manual_bonus = 45 if candidate.source == "manual" else 0
        common_bonus = 30 if rank < 800 else 18 if rank < 1800 else 8
        stroke_bonus = max(0, 22 - stroke)
        recent_penalty = 20 if candidate.char in recent_chars else 0
        score = manual_bonus + common_bonus + stroke_bonus - recent_penalty - rank / 400
        scored.append(
            Candidate(
                char=candidate.char,
                key=candidate.key,
                plain=candidate.plain,
                tone=candidate.tone,
                stroke_count=candidate.stroke_count,
                is_polyphonic=candidate.is_polyphonic,
                source=candidate.source,
                score=score,
            )
        )
    return sorted(scored, key=lambda item: (item.score, -(item.stroke_count or 99)), reverse=True)


def fix_blocked_words(output_chars: list[str], items: list[ReplaceItem], blocked_words: set[str]) -> int:
    fallbacks = 0
    output = "".join(output_chars)
    for word in blocked_words:
        at = output.find(word)
        while at != -1:
            target_index = find_changed_index_in_range(items, at, at + len(word))
            if target_index == -1:
                break
            item = items[target_index]
            output_chars[target_index] = item.origin
            item.replacement = item.origin
            item.changed = False
            item.reason = "blocked"
            fallbacks += 1
            output = "".join(output_chars)
            at = output.find(word)
    return fallbacks


def find_changed_index_in_range(items: list[ReplaceItem], start: int, end: int) -> int:
    for index in range(end - 1, start - 1, -1):
        if 0 <= index < len(items) and items[index].changed:
            return index
    return -1
