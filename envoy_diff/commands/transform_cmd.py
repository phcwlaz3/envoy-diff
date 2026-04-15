"""CLI subcommand for transforming env config keys and values."""

import argparse
import json
import sys
from typing import List, Optional

from envoy_diff.loader import load_config, UnsupportedFormatError
from envoy_diff.transformer import transform_config


def add_transform_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "transform",
        help="Apply transformations to an env config file.",
    )
    parser.add_argument("file", help="Path to the env or JSON config file.")
    parser.add_argument(
        "--apply",
        nargs="+",
        default=[],
        metavar="TRANSFORM",
        help="Named transforms to apply: uppercase_keys, strip_values.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        metavar="PREFIX",
        help="Prefix to prepend to all keys after other transforms.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_transform_command)


def run_transform_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = transform_config(
        config,
        transforms=args.apply,
        prefix=args.prefix,
    )

    if args.format == "json":
        output = {
            "config": result.config,
            "applied": result.applied,
            "skipped": result.skipped,
            "transform_count": result.transform_count,
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        print()
        for key, value in sorted(result.config.items()):
            print(f"{key}={value}")

    return 0
