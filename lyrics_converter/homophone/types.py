from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HomophoneOptions:
    strict_tone: bool = True
    avoid_polyphonic: bool = True
    avoid_complex_chars: bool = True
    max_strokes: int = 12
    allow_original: bool = True


@dataclass(frozen=True)
class Pronunciation:
    char: str
    key: str
    plain: str
    tone: int


@dataclass(frozen=True)
class Candidate:
    char: str
    key: str
    plain: str
    tone: int
    stroke_count: int | None = None
    is_polyphonic: bool = False
    source: str = "auto"
    score: float = 0


@dataclass
class ReplaceItem:
    index: int
    origin: str
    replacement: str
    pinyin: str
    changed: bool
    reason: str
    candidates: list[str] = field(default_factory=list)


@dataclass
class ReplaceStats:
    total_chinese: int = 0
    replaced: int = 0
    kept_original: int = 0
    non_chinese: int = 0
    blocked_fallbacks: int = 0


@dataclass
class ReplaceResult:
    input: str
    output: str
    items: list[ReplaceItem]
    stats: ReplaceStats
