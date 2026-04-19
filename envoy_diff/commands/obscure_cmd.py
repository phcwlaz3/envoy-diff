"""CLI sub-command: obscure — partially mask sensitive config values."""
from __future__ import annotations
import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.obscurer import obscure_config


def add_obscure_subparsers(subparsers) -> None:
    parser = subparsers.add_parser("obscure", help="Partially mask sensitive config values.")
    parser.add_argument("file", help="Path to .env or .json config file.")
    parser.add_argument(
        "--visible-chars",
        type=int,
        default=4,
        dest="visible_chars",
        help="Number of characters to keep visible (default: 4).",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        metavar="PATTERN",
        help="Regex pattern to match sensitive keys (repeatable).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_obscure_command)


def run_obscure_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = obscure_config(
        config,
        patterns=args.patterns or None,
        visible_chars=args.visible_chars,
    )

    if args.fmt == "json":
        out = {
            "obscured": result.obscured,
            "obscured_keys": result.obscured_keys,
            "obscure_count": result.obscure_count(),
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        if result.has_obscured():
            print("\nObscured keys:")
            for key in result.obscured_keys:
                print(f"  {key}: {result.obscured[key]}")
        print("\nFull config:")
        for key, value in result.obscured.items():
            print(f"  {key}={value}")

    return 0
