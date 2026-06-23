from __future__ import annotations

from typing import Any

from lyrics_converter.registry import get_converter


def convert_text(
    mode: str,
    text: str,
    custom_dict: dict[str, list[str] | str] | None = None,
    options: dict[str, Any] | None = None,
) -> str:
    converter = get_converter(mode)
    return converter.convert(text, custom_dict=custom_dict or {}, options=options or {})
