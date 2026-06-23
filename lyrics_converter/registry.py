from __future__ import annotations

from lyrics_converter.converters.base import LyricsConverter
from lyrics_converter.converters.cantonese import CantoneseJyutpingConverter
from lyrics_converter.converters.english import EnglishPhoneticConverter
from lyrics_converter.converters.homophone import HomophoneReplaceConverter
from lyrics_converter.converters.mandarin import MandarinPinyinConverter
from lyrics_converter.converters.minnan import MinnanTailoConverter


_CONVERTERS: dict[str, LyricsConverter] = {
    converter.metadata.id: converter
    for converter in (
        MandarinPinyinConverter(),
        CantoneseJyutpingConverter(),
        EnglishPhoneticConverter(),
        MinnanTailoConverter(),
        HomophoneReplaceConverter(),
    )
}


def list_converters(include_unimplemented: bool = True) -> list[LyricsConverter]:
    converters = list(_CONVERTERS.values())
    if include_unimplemented:
        return converters
    return [converter for converter in converters if converter.metadata.implemented]


def get_converter(converter_id: str) -> LyricsConverter:
    try:
        return _CONVERTERS[converter_id]
    except KeyError as exc:
        known = ", ".join(sorted(_CONVERTERS))
        raise ValueError(f"unknown mode: {converter_id}. Known modes: {known}") from exc
