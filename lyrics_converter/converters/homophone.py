from __future__ import annotations

from typing import Any

from lyrics_converter.converters.base import ConverterMetadata, ConverterOption, LyricsConverter
from lyrics_converter.homophone import HomophoneOptions, replace_homophones


class HomophoneReplaceConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="homophone",
        name="谐音字替换",
        description="将中文歌词逐字替换为同音或同音同调的其他汉字。",
        options=(
            ConverterOption(
                key="homophone_strict_tone",
                label="严格匹配声调",
                default=True,
                help="开启后只使用同拼音、同声调的替换字。",
            ),
            ConverterOption(
                key="homophone_avoid_polyphonic",
                label="避开多音字",
                default=True,
                help="过滤候选中的多音字，减少误读。",
            ),
            ConverterOption(
                key="homophone_avoid_complex",
                label="避开复杂字",
                default=True,
                help="过滤笔画数过高或未收录笔画数的候选字。",
            ),
            ConverterOption(
                key="homophone_max_strokes",
                label="最大笔画数",
                kind="number",
                default=12,
                help="避开复杂字开启时生效。",
            ),
        ),
    )

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        options = options or {}
        homophone_options = HomophoneOptions(
            strict_tone=bool(options.get("homophone_strict_tone", True)),
            avoid_polyphonic=bool(options.get("homophone_avoid_polyphonic", True)),
            avoid_complex_chars=bool(options.get("homophone_avoid_complex", True)),
            max_strokes=int(options.get("homophone_max_strokes", 12)),
        )
        result = replace_homophones(text, homophone_options)
        return result.output
