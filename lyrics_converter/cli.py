from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lyrics_converter.core import convert_text
from lyrics_converter.registry import list_converters
from lyrics_converter.utils import load_json_dict


def build_parser() -> argparse.ArgumentParser:
    converters = list_converters(include_unimplemented=True)
    mode_choices = [converter.metadata.id for converter in converters]

    parser = argparse.ArgumentParser(description="Convert lyrics to romanized or phonetic lyrics.")
    parser.add_argument("--mode", choices=mode_choices, help="conversion mode")
    parser.add_argument("input", nargs="?", help="input lyric text file")
    parser.add_argument("output", nargs="?", help="output text file; prints to stdout when omitted")
    parser.add_argument("--custom-dict", help="JSON dictionary for phrase/word overrides")
    parser.add_argument(
        "--no-english-sections",
        action="store_true",
        help="do not add heuristic Verse/Chorus/Bridge/Outro labels in English mode",
    )
    parser.add_argument(
        "--tailo-format",
        choices=["mark", "number", "strip"],
        default="mark",
        help="Tailo tone format for minnan mode",
    )
    parser.add_argument(
        "--tailo-dialect",
        choices=["south", "north", "singapore"],
        default="south",
        help="Tailo dialect preference for minnan mode",
    )
    parser.add_argument(
        "--homophone-ignore-tone",
        action="store_true",
        help="allow same pinyin with different tone in homophone mode",
    )
    parser.add_argument(
        "--homophone-allow-polyphonic",
        action="store_true",
        help="allow polyphonic candidate characters in homophone mode",
    )
    parser.add_argument(
        "--homophone-allow-complex",
        action="store_true",
        help="allow complex or unknown-stroke candidate characters in homophone mode",
    )
    parser.add_argument(
        "--homophone-max-strokes",
        type=int,
        default=12,
        help="maximum stroke count for homophone candidates",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="show available conversion modes and exit",
    )
    return parser


def print_modes() -> None:
    for converter in list_converters(include_unimplemented=True):
        status = "ready" if converter.metadata.implemented else "planned"
        print(f"{converter.metadata.id}\t{status}\t{converter.metadata.name}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_modes:
        print_modes()
        return 0

    if not args.mode or not args.input:
        parser.error("--mode and input are required unless --list-modes is used")

    input_path = Path(args.input)
    text = input_path.read_text(encoding="utf-8")
    custom = load_json_dict(args.custom_dict)
    options = {
        "add_sections": not args.no_english_sections,
        "tailo_format": args.tailo_format,
        "tailo_dialect": args.tailo_dialect,
        "homophone_strict_tone": not args.homophone_ignore_tone,
        "homophone_avoid_polyphonic": not args.homophone_allow_polyphonic,
        "homophone_avoid_complex": not args.homophone_allow_complex,
        "homophone_max_strokes": args.homophone_max_strokes,
    }
    converted = convert_text(args.mode, text, custom_dict=custom, options=options)

    if args.output:
        Path(args.output).write_text(converted, encoding="utf-8")
    else:
        print(converted)
    return 0


def run() -> None:
    try:
        raise SystemExit(main())
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    run()
