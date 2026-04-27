"""CLI sub-command: envoy-diff swap."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.swapper import swap_config


def _parse_pairs(raw: List[str]):
    """Parse 'KEY_A:KEY_B' strings into (key_a, key_b) tuples."""
    pairs = []
    for item in raw:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid swap pair {item!r}. Expected format KEY_A:KEY_B"
            )
        a, _, b = item.partition(":")
        pairs.append((a.strip(), b.strip()))
    return pairs


def add_swap_subparsers(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "swap",
        help="Swap values between pairs of keys in an env file.",
    )
    parser.add_argument("file", help="Path to the env/json config file.")
    parser.add_argument(
        "--pair",
        dest="pairs",
        metavar="KEY_A:KEY_B",
        action="append",
        default=[],
        help="Key pair to swap (repeatable). Format: KEY_A:KEY_B",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_swap_command)


def run_swap_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    try:
        pairs = _parse_pairs(args.pairs)
    except argparse.ArgumentTypeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = swap_config(config, pairs=pairs)

    if args.format == "json":
        output = {
            "config": result.config,
            "swapped": [[a, b] for a, b in result.swapped],
            "skipped": result.skipped,
            "swap_count": result.swap_count(),
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.has_swaps():
            print()
            for key, value in result.config.items():
                print(f"{key}={value}")

    return 0
