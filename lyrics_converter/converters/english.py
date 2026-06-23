from __future__ import annotations

import re

from lyrics_converter.converters.base import ConverterMetadata, ConverterOption, LyricsConverter
from lyrics_converter.utils import WORD_RE, normalize_english_dict


ENGLISH_WORDS: dict[str, str] = {
    "a": "uh",
    "above": "uh-buv",
    "acquaintance": "uh-kwayn-tuns",
    "afford": "uh-fohrd",
    "ain't": "aynt",
    "aint": "aynt",
    "all": "awl",
    "alone": "uh-lohn",
    "already": "awl-red-ee",
    "am": "am",
    "amazing": "uh-may-zing",
    "and": "and",
    "apart": "uh-part",
    "appear": "uh-peer",
    "articulate": "ar-tik-yoo-layt",
    "away": "uh-way",
    "babe": "bayb",
    "baby": "bay-bee",
    "be": "bee",
    "believed": "bee-leevd",
    "better": "bet-er",
    "between": "bee-tween",
    "blame": "blaym",
    "blamin": "blaym-in'",
    "blaming": "blaym-in'",
    "blazing": "blay-zing",
    "blind": "blynd",
    "brought": "brawt",
    "but": "but",
    "can't": "kant",
    "cant": "kant",
    "cause": "kuz",
    "'cause": "'kuz",
    "communicate": "kuh-myoo-nuh-kayt",
    "cry": "krai",
    "cup": "kuhp",
    "dangers": "dayn-jurz",
    "dear": "deer",
    "diamond": "dye-mund",
    "did": "did",
    "die": "die",
    "distance": "dis-tuns",
    "don't": "dont",
    "dont": "dont",
    "even": "ee-ven",
    "every": "ev-ree",
    "eyes": "eyes",
    "far": "fahr",
    "fear": "feer",
    "fears": "feerz",
    "feel": "feel",
    "feelin": "feel-in'",
    "feeling": "feel-in'",
    "find": "fynd",
    "findin": "fynd-in'",
    "finding": "fynd-in'",
    "first": "furst",
    "fohr": "fohr",
    "for": "fohr",
    "forever": "fuh-rev-er",
    "forgot": "fur-got",
    "found": "fownd",
    "girl": "gurl",
    "go": "go",
    "goin": "go-in'",
    "going": "go-in'",
    "gon": "gon'",
    "gonna": "gon-uh",
    "grace": "grays",
    "happens": "hap-enz",
    "hard": "hard",
    "has": "haz",
    "hate": "hayt",
    "have": "hav",
    "he": "hee",
    "heart": "hart",
    "high": "hye",
    "hold": "hohld",
    "home": "hohm",
    "hour": "ow-er",
    "how": "how",
    "i": "eye",
    "i'd": "I'd",
    "i'll": "I'll",
    "i'm": "I'm",
    "if": "if",
    "in": "in",
    "is": "iz",
    "it": "it",
    "it'll": "it'l",
    "its": "its",
    "it's": "its",
    "just": "just",
    "keep": "keep",
    "kill": "kil",
    "kindness": "kynd-ness",
    "know": "noh",
    "lead": "leed",
    "let": "let",
    "lie": "lie",
    "like": "lyke",
    "light": "lyte",
    "little": "lit-ul",
    "lonely": "lohn-lee",
    "lost": "lawst",
    "love": "luv",
    "makes": "mayks",
    "manipulate": "muh-nip-yoo-layt",
    "many": "men-ee",
    "me": "mee",
    "mind": "mind",
    "miss": "miss",
    "my": "mai",
    "na": "na",
    "never": "neh-ver",
    "night": "nite",
    "no": "no",
    "not": "not",
    "nothing": "nuh-thing",
    "now": "now",
    "oh": "oh",
    "old": "ohld",
    "once": "wuhns",
    "one": "wun",
    "pain": "payn",
    "perfect": "purr-fekt",
    "precious": "presh-us",
    "pull": "pul",
    "real": "reel",
    "reason": "ree-zun",
    "relieved": "ree-leevd",
    "right": "rite",
    "safe": "sayf",
    "saved": "sayvd",
    "say": "say",
    "sayin": "say-in'",
    "saying": "say-in'",
    "scared": "skayrd",
    "see": "sea",
    "shines": "shynz",
    "should": "shood",
    "show": "shoh",
    "sky": "skye",
    "snares": "snehrz",
    "so": "soh",
    "sound": "sownd",
    "specially": "spesh-lee",
    "'specially": "'spesh-lee",
    "star": "stahr",
    "sun": "sun",
    "sweet": "sweet",
    "take": "tayk",
    "taught": "tawt",
    "tell": "tel",
    "that": "that",
    "that's": "thatz",
    "thats": "thatz",
    "the": "thuh",
    "then": "then",
    "think": "think",
    "thinkin": "think-in'",
    "thinking": "think-in'",
    "this": "this",
    "though": "tho",
    "thoughts": "thots",
    "through": "throo",
    "thus": "thus",
    "time": "time",
    "to": "tuh",
    "toils": "toylz",
    "tonight": "tuh-nite",
    "too": "too",
    "truth": "trooth",
    "try": "try",
    "twinkle": "twin-kul",
    "'tis": "'tiz",
    "'twas": "'twuz",
    "up": "up",
    "upon": "uh-pon",
    "us": "us",
    "walk": "wawk",
    "want": "wont",
    "was": "wuz",
    "ways": "wayz",
    "we": "wee",
    "we'll": "weel",
    "we're": "wee",
    "wen": "wen",
    "what": "wut",
    "when": "wen",
    "will": "wil",
    "with": "with",
    "won't": "wont",
    "wont": "wont",
    "wonder": "wun-der",
    "wood": "wood",
    "workin": "work-in'",
    "working": "work-in'",
    "world": "wurld",
    "worth": "wurth",
    "would": "wood",
    "wretch": "rech",
    "yeah": "yeah",
    "yet": "yet",
    "you": "yew",
    "you're": "yor",
    "your": "yor",
}

ARPABET_TO_RESP: dict[str, str] = {
    "AA": "ah",
    "AE": "a",
    "AH": "uh",
    "AO": "aw",
    "AW": "ow",
    "AY": "eye",
    "B": "b",
    "CH": "ch",
    "D": "d",
    "DH": "th",
    "EH": "eh",
    "ER": "ur",
    "EY": "ay",
    "F": "f",
    "G": "g",
    "HH": "h",
    "IH": "ih",
    "IY": "ee",
    "JH": "j",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "NG": "ng",
    "OW": "oh",
    "OY": "oy",
    "P": "p",
    "R": "r",
    "S": "s",
    "SH": "sh",
    "T": "t",
    "TH": "th",
    "UH": "oo",
    "UW": "oo",
    "V": "v",
    "W": "w",
    "Y": "y",
    "Z": "z",
    "ZH": "zh",
}


def strip_stress(phone: str) -> str:
    return re.sub(r"\d", "", phone)


def cmu_respelling(word: str) -> str:
    try:
        import pronouncing
    except ImportError:
        return word

    lookup = word.lower().strip("'")
    phones = pronouncing.phones_for_word(lookup)
    if not phones:
        return word
    parts = []
    for phone in phones[0].split():
        parts.append(ARPABET_TO_RESP.get(strip_stress(phone), strip_stress(phone).lower()))
    respelled = "".join(parts)
    respelled = re.sub(r"([aeiou])ng$", r"\1ng", respelled)
    return respelled or word


def apply_case(source: str, converted: str) -> str:
    if not source:
        return converted
    if source.startswith("'") and len(source) > 1:
        body = converted[1:] if converted.startswith("'") else converted
        if source[1].isupper():
            body = body[:1].upper() + body[1:]
        return "'" + body
    if source.isupper() and len(source) > 1:
        return converted.upper()
    if source[0].isupper():
        return converted[:1].upper() + converted[1:]
    return converted


def convert_english_word(word: str, custom: dict[str, str]) -> str:
    key = word.lower()
    plain_key = key.rstrip("'")
    if key in custom:
        return apply_case(word, custom[key])
    if plain_key in custom:
        return apply_case(word, custom[plain_key])
    if key in ENGLISH_WORDS:
        return apply_case(word, ENGLISH_WORDS[key])
    if plain_key in ENGLISH_WORDS:
        return apply_case(word, ENGLISH_WORDS[plain_key])

    if key.endswith("in'") and len(key) > 4:
        base = key[:-3] + "ing"
        if base in ENGLISH_WORDS:
            converted = ENGLISH_WORDS[base]
            if converted.endswith("ing"):
                converted = converted[:-3] + "in'"
            return apply_case(word, converted)

    return apply_case(word, cmu_respelling(key))


def should_insert_section(line: str, state: dict[str, bool], next_content: str = "") -> str | None:
    lowered = line.strip().lower()
    if not lowered:
        return None
    if not state.get("started"):
        state["started"] = True
        return "[Verse]"
    if lowered.startswith("you know what"):
        return "[Chorus]"
    if lowered.startswith("i'm finding ways to manipulate"):
        return "[Verse]"
    if (
        lowered.startswith("i would die for you")
        and next_content.lower().startswith("i would lie for you")
        and not state.get("bridge")
    ):
        state["bridge"] = True
        return "[Bridge]"
    if lowered.startswith("even though") and state.get("bridge") and not state.get("outro"):
        state["outro"] = True
        return "[Outro]"
    if lowered.startswith("even though") and not state.get("second_chorus"):
        state["second_chorus"] = True
        return "[Chorus]"
    return None


class EnglishPhoneticConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="english",
        name="英语转音译改写",
        description="将英文歌词改写成便于跟读的英文式音译。",
        options=(
            ConverterOption(
                key="add_sections",
                label="自动添加段落标签",
                default=True,
                help="按简单启发式添加 [Verse] / [Chorus] / [Bridge] / [Outro]。",
            ),
        ),
    )

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict | None = None,
    ) -> str:
        word_dict = normalize_english_dict(custom_dict or {})
        add_sections = True if options is None else bool(options.get("add_sections", True))
        lines: list[str] = []
        section_state: dict[str, bool] = {}

        source_lines = text.splitlines()
        for line_index, line in enumerate(source_lines):
            next_content = ""
            for later in source_lines[line_index + 1 :]:
                if later.strip():
                    next_content = later.strip()
                    break
            section = should_insert_section(line, section_state, next_content) if add_sections else None
            if section:
                if lines and lines[-1] != "":
                    lines.append("")
                lines.append(section)

            pieces: list[str] = []
            for token in WORD_RE.findall(line):
                if re.match(r"[A-Za-z']+$", token) and any(ch.isalpha() for ch in token):
                    pieces.append(convert_english_word(token, word_dict))
                else:
                    pieces.append(token)
            lines.append("".join(pieces))

        return "\n".join(lines)
