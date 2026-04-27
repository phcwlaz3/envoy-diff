"""CLI sub-command: duplicate — copy config keys under new names."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.duplicator import duplicate_config


def _parse_pairs(raw: List[str]) -> dict:
    """Parse 'SOURCE:TARGET' strings into a mapping dict."""
    mapping = {}
    for item in raw:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid mapping '{item}': expected SOURCE:TARGET format."
            )
        source, _, target = item.partition(":")
        mapping[source.strip()] = target.strip()
    return mapping


def add_duplicate_subparsers(subparsers) -> None:
    parser = subparsers.add_parser(
        "duplicate",
        help="Copy config keys under new names.",
    )
    parser.add_argument("file", help="Path to the env/JSON config file.")
    parser.add_argument(
        "--map",
        dest="pairs",
        metavar="SOURCE:TARGET",
        nargs="+",
        required=True,
        help="One or more SOURCE:TARGET key pairs to duplicate.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the target key if it already exists.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )


def run_duplicate_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    try:
        mapping = _parse_pairs(args.pairs)
    except argparse.ArgumentTypeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = duplicate_config(config, mapping, overwrite=args.overwrite)

    if args.format == "json":
        output = {
            "config": result.config,
            "duplicated": result.duplicated,
            "skipped": result.skipped,
            "duplicate_count": result.duplicate_count(),
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        for source in result.duplicated:
            target = mapping[source]
            print(f"  {source} -> {target} = {result.config[target]!r}")
        if result.skipped:
            print(f"Skipped: {', '.join(result.skipped)}")

    return 0
