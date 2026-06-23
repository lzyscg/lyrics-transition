from __future__ import annotations

from lyrics_converter.converters.base import ConverterMetadata, LyricsConverter
from lyrics_converter.utils import non_cjk_to_units, normalize_phrase_dict, render_units, split_cjk_runs


CANTONESE_PHRASES: dict[str, list[str]] = {
    "誰": ["seoi4"],
    "谁": ["seoi4"],
    "著": ["zo6"],
    "着": ["zo6"],
}


class CantoneseJyutpingConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="cantonese",
        name="粤语转拼音",
        description="将粤语歌词转换为 Jyutping 粤拼和声调数字。",
    )

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict | None = None,
    ) -> str:
        try:
            import pycantonese
            from opencc import OpenCC
        except ImportError as exc:
            raise RuntimeError("Missing dependency: install pycantonese and opencc-python-reimplemented") from exc

        converter = OpenCC("s2hk")
        phrase_dict = dict(CANTONESE_PHRASES)
        phrase_dict.update(normalize_phrase_dict(custom_dict or {}))

        def fallback(char: str) -> list[str]:
            traditional = converter.convert(char)
            converted = pycantonese.characters_to_jyutping(traditional)
            if converted and converted[0][1]:
                return converted[0][1].split()
            return [char]

        def convert_run(run: str) -> list[str]:
            result: list[str] = []
            index = 0
            max_len = max((len(key) for key in phrase_dict), default=0)
            while index < len(run):
                matched = False
                for size in range(min(max_len, len(run) - index), 0, -1):
                    chunk = run[index : index + size]
                    trad_chunk = converter.convert(chunk)
                    if chunk in phrase_dict or trad_chunk in phrase_dict:
                        result.extend(phrase_dict.get(chunk, phrase_dict[trad_chunk]))
                        index += size
                        matched = True
                        break
                if matched:
                    continue

                remaining = run[index:]
                converted = pycantonese.characters_to_jyutping(converter.convert(remaining))
                if converted and converted[0][1]:
                    source, jyutping = converted[0]
                    result.extend(jyutping.split())
                    index += len(source)
                else:
                    result.extend(fallback(run[index]))
                    index += 1
            return result

        lines: list[str] = []
        for line in text.splitlines():
            units: list[tuple[str, str]] = []
            for cjk, chunk in split_cjk_runs(line) or []:
                if cjk:
                    units.extend(("word", item) for item in convert_run(chunk))
                else:
                    units.extend(non_cjk_to_units(chunk))
            lines.append(render_units(units))
        return "\n".join(lines)
