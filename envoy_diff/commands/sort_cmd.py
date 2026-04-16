"""CLI subcommand: sort — sort config keys by a chosen strategy."""
from __future__ import annotations
import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.sorter import sort_config


def add_sort_subparsers(subparsers) -> None:
    parser = subparsers.add_parser("sort", help="Sort config keys by a strategy")
    parser.add_argument("file", help="Path to .env or .json config file")
    parser.add_argument(
        "--strategy",
        choices=["alpha", "length", "value_length"],
        default="alpha",
        help="Sort strategy (default: alpha)",
    )
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )


def run_sort_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    try:
        result = sort_config(config, strategy=args.strategy, reverse=args.reverse)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        print(json.dumps({"strategy": result.strategy, "config": result.config}, indent=2))
    else:
        print(result.summary())
        for key, value in result.config.items():
            print(f"  {key}={value}")

    return 0
