"""CLI sub-command: normalize — clean up env config values in place."""

from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.normalizer import normalize_config


def add_normalize_subparsers(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "normalize",
        help="Normalize env config values (strip quotes, whitespace, booleans).",
    )
    parser.add_argument("file", help="Path to the env or JSON config file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--no-strip-quotes",
        action="store_true",
        default=False,
        help="Disable quote stripping.",
    )
    parser.add_argument(
        "--no-booleans",
        action="store_true",
        default=False,
        help="Disable boolean canonicalization.",
    )
    parser.add_argument(
        "--no-whitespace",
        action="store_true",
        default=False,
        help="Disable whitespace stripping.",
    )
    parser.set_defaults(func=run_normalize_command)


def run_normalize_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = normalize_config(
        config,
        strip_quotes=not args.no_strip_quotes,
        normalize_booleans=not args.no_booleans,
        strip_whitespace=not args.no_whitespace,
    )

    if args.fmt == "json":
        payload = {
            "normalized": result.normalized,
            "changes": result.changes,
            "change_count": result.change_count,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        if result.change_count:
            print("\nNormalized config:")
            for key, value in result.normalized.items():
                print(f"  {key}={value}")

    return 0
