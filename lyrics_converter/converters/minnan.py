from __future__ import annotations

from typing import Any

from lyrics_converter.converters.base import ConverterMetadata, ConverterOption, LyricsConverter


TAILO_FORMATS = {
    "mark": "mark",
    "number": "number",
    "strip": "strip",
}

TAILO_DIALECTS = {
    "south": "south",
    "north": "north",
    "singapore": "singapore",
}


class MinnanTailoConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="minnan",
        name="闽南语转台罗拼音",
        description="将闽南语/台语歌词转换为台罗拼音。",
        implemented=True,
        options=(
            ConverterOption(
                key="tailo_format",
                label="声调格式",
                kind="select",
                default="mark",
                help="mark=调号符号，number=数字声调，strip=无声调。",
            ),
            ConverterOption(
                key="tailo_dialect",
                label="腔调",
                kind="select",
                default="south",
                help="south=偏漳州/南部，north=偏泉州/北部，singapore=新加坡。",
            ),
        ),
    )

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        try:
            from taibun import Converter
        except ImportError as exc:
            raise RuntimeError("Missing dependency: install taibun") from exc

        options = options or {}
        tailo_format = str(options.get("tailo_format", "mark"))
        tailo_dialect = str(options.get("tailo_dialect", "south"))
        if tailo_format not in TAILO_FORMATS:
            raise ValueError(f"Unsupported Tailo format: {tailo_format}")
        if tailo_dialect not in TAILO_DIALECTS:
            raise ValueError(f"Unsupported Tailo dialect: {tailo_dialect}")

        converter = Converter(
            system="Tailo",
            dialect=tailo_dialect,
            format=tailo_format,
            punctuation="none",
        )

        replacements = build_replacements(custom_dict or {}, converter)
        lines: list[str] = []
        for line in text.splitlines():
            if not line.strip():
                lines.append("")
                continue
            converted = converter.get(line)
            for source, target in replacements.items():
                converted = converted.replace(source, target)
            lines.append(converted.strip())
        return "\n".join(lines)


def build_replacements(data: dict[str, list[str] | str], converter) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, str):
            target = value
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            target = " ".join(value)
        else:
            raise ValueError(f"custom dict value for {key!r} must be a string or a string list")
        result[key] = target
        converted_key = converter.get(key).strip()
        if converted_key and converted_key != key:
            result[converted_key] = target
    return result
