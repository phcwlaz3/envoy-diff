from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from envoy_diff.loader import load_config
from envoy_diff.coercer import coerce_config


def add_coerce_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "coerce",
        help="Auto-coerce environment variable values to their natural types.",
    )
    parser.add_argument("file", help="Path to the env or JSON config file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any coercions failed.",
    )


def run_coerce_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = coerce_config(config)

    if args.format == "json":
        output = {
            "coerced": result.coerced,
            "failures": result.failures,
            "coerce_count": result.coerce_count(),
            "has_failures": result.has_failures(),
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.coerced:
            print("\nCoerced keys:")
            for key, value in result.coerced.items():
                print(f"  {key}: {value!r}")
        if result.failures:
            print("\nFailed coercions:")
            for key, reason in result.failures.items():
                print(f"  {key}: {reason}")

    if args.strict and result.has_failures():
        return 1
    return 0
