"""CLI sub-command: flatten a nested JSON config into dot-notation keys."""
from __future__ import annotations
import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.flattener import flatten_config


def add_flatten_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "flatten",
        help="Flatten a nested JSON config into dot-notation keys.",
    )
    parser.add_argument("file", help="Path to a JSON config file.")
    parser.add_argument(
        "--sep",
        default=".",
        help="Separator for nested keys (default: '.').",
    )
    parser.add_argument(
        "--uppercase",
        action="store_true",
        help="Convert keys to UPPER_SNAKE_CASE after flattening.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )


def run_flatten_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = flatten_config(config, sep=args.sep, uppercase_keys=args.uppercase)

    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "summary": result.summary,
                    "original_key_count": result.original_key_count,
                    "flattened_key_count": result.flattened_key_count,
                    "config": result.config,
                },
                indent=2,
            )
        )
    else:
        print(result.summary)
        for k, v in sorted(result.config.items()):
            print(f"  {k}={v}")

    return 0
