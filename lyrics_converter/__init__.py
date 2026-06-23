"""Lyrics conversion package."""

from lyrics_converter.core import convert_text
from lyrics_converter.registry import get_converter, list_converters

__all__ = ["convert_text", "get_converter", "list_converters"]
