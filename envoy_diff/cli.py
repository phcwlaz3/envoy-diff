"""CLI entry point for envoy-diff."""

import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.differ import diff_configs
from envoy_diff.formatter import format_diff
from envoy_diff.loader import UnsupportedFormatError, load_config
from envoy_diff.validator import validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Diff and validate environment variable configs across deployment stages.",
    )
    parser.add_argument("base", help="Base config file (.env or .json)")
    parser.add_argument("target", help="Target config file (.env or .json)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--require",
        metavar="KEY",
        nargs="+",
        help="Required keys that must be present in both configs",
    )
    parser.add_argument(
        "--ignore-empty",
        metavar="KEY",
        nargs="+",
        help="Keys to ignore when checking for empty values",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code if differences or validation errors are found",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        base_config = load_config(args.base)
        target_config = load_config(args.target)
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 2

    required_keys = set(args.require) if args.require else None
    ignore_empty = set(args.ignore_empty) if args.ignore_empty else None

    has_errors = False
    for label, config in (("base", base_config), ("target", target_config)):
        result = validate_config(config, required_keys=required_keys, ignore_empty_keys=ignore_empty)
        for err in result.errors:
            print(f"[{label}] ERROR: {err}", file=sys.stderr)
            has_errors = True
        for warn in result.warnings:
            print(f"[{label}] WARNING: {warn}", file=sys.stderr)

    diff = diff_configs(base_config, target_config)
    print(format_diff(diff, fmt=args.format))

    if args.exit_code and (has_errors or diff.has_diff):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
