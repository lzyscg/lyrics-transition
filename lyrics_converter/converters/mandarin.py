from __future__ import annotations

from lyrics_converter.converters.base import ConverterMetadata, LyricsConverter
from lyrics_converter.utils import (
    longest_match_convert,
    non_cjk_to_units,
    normalize_phrase_dict,
    render_units,
    split_cjk_runs,
)


MANDARIN_PHRASES: dict[str, list[str]] = {
    "不了": ["bù", "le"],
    "敕勒": ["chì", "lè"],
    "草低见牛羊": ["cǎo", "dī", "xiàn", "niú", "yáng"],
}


class MandarinPinyinConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="mandarin",
        name="国语转拼音",
        description="将国语/普通话歌词转换为带声调拼音。",
    )

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict | None = None,
    ) -> str:
        try:
            from pypinyin import Style, pinyin
        except ImportError as exc:
            raise RuntimeError("Missing dependency: install pypinyin") from exc

        phrase_dict = dict(MANDARIN_PHRASES)
        phrase_dict.update(normalize_phrase_dict(custom_dict or {}))

        def fallback(char: str) -> list[str]:
            converted = pinyin(char, style=Style.TONE, heteronym=False, neutral_tone_with_five=False)
            return [converted[0][0]] if converted and converted[0] else [char]

        lines: list[str] = []
        for line in text.splitlines():
            units: list[tuple[str, str]] = []
            for cjk, chunk in split_cjk_runs(line) or []:
                if cjk:
                    units.extend(("word", item) for item in longest_match_convert(chunk, phrase_dict, fallback))
                else:
                    units.extend(non_cjk_to_units(chunk))
            lines.append(render_units(units))
        return "\n".join(lines)
