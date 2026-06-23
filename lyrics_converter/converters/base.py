from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConverterOption:
    key: str
    label: str
    kind: str = "checkbox"
    default: Any = None
    help: str = ""


@dataclass(frozen=True)
class ConverterMetadata:
    id: str
    name: str
    description: str
    implemented: bool = True
    options: tuple[ConverterOption, ...] = field(default_factory=tuple)


class LyricsConverter:
    metadata: ConverterMetadata

    def convert(
        self,
        text: str,
        custom_dict: dict[str, list[str] | str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError
