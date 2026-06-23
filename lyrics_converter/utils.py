from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Iterable


WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?'?|'[A-Za-z]+|[0-9]+|[^\w\s]|\s+", re.UNICODE)


def load_json_dict(path: str | None) -> dict[str, list[str] | str]:
    if not path:
        return {}
    return parse_json_dict(Path(path).read_text(encoding="utf-8"))


def parse_json_dict(raw: str) -> dict[str, list[str] | str]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("custom dict must be a JSON object")
    return data


def is_cjk(char: str) -> bool:
    code = ord(char)
    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
    )


def split_cjk_runs(line: str) -> Iterable[tuple[bool, str]]:
    if not line:
        return
    start = 0
    current_is_cjk = is_cjk(line[0])
    for index, char in enumerate(line[1:], start=1):
        char_is_cjk = is_cjk(char)
        if char_is_cjk != current_is_cjk:
            yield current_is_cjk, line[start:index]
            start = index
            current_is_cjk = char_is_cjk
    yield current_is_cjk, line[start:]


def render_units(units: list[tuple[str, str]]) -> str:
    output: list[str] = []
    previous_kind = ""

    for kind, value in units:
        if not value:
            continue
        if kind == "space":
            if output and output[-1] != " ":
                output.append(" ")
            previous_kind = kind
            continue
        if kind == "word":
            if output and output[-1] not in " (":
                output.append(" ")
            output.append(value)
        elif kind == "open":
            if output and output[-1] != " ":
                output.append(" ")
            output.append(value)
        elif kind == "close":
            while output and output[-1] == " ":
                output.pop()
            output.append(value)
        else:
            output.append(value)
        previous_kind = kind

    return "".join(output).strip()


def non_cjk_to_units(text: str) -> list[tuple[str, str]]:
    units: list[tuple[str, str]] = []
    for char in text:
        if char.isspace():
            units.append(("space", " "))
        elif char in "([{":
            units.append(("open", char))
        elif char in ")]}":
            units.append(("close", char))
        else:
            units.append(("punct", char))
    return units


def longest_match_convert(
    text: str,
    phrase_dict: dict[str, list[str]],
    fallback: Callable[[str], list[str]],
) -> list[str]:
    result: list[str] = []
    index = 0
    max_len = max((len(key) for key in phrase_dict), default=0)
    while index < len(text):
        matched = False
        for size in range(min(max_len, len(text) - index), 0, -1):
            chunk = text[index : index + size]
            if chunk in phrase_dict:
                result.extend(phrase_dict[chunk])
                index += size
                matched = True
                break
        if not matched:
            result.extend(fallback(text[index]))
            index += 1
    return result


def normalize_phrase_dict(data: dict[str, list[str] | str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = value.split()
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            result[key] = value
        else:
            raise ValueError(f"custom dict value for {key!r} must be a string or a string list")
    return result


def normalize_english_dict(data: dict[str, list[str] | str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key.lower()] = value
        elif isinstance(value, list):
            result[key.lower()] = "-".join(str(item) for item in value)
        else:
            raise ValueError(f"custom dict value for {key!r} must be a string or a string list")
    return result
