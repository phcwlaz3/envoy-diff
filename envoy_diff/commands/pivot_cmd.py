"""CLI sub-command: pivot — group env keys by prefix into a nested view."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.pivotter import pivot_config


def add_pivot_subparsers(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "pivot",
        help="Pivot env config keys into nested groups by prefix.",
    )
    parser.add_argument("file", help="Path to env or JSON config file.")
    parser.add_argument(
        "--separator",
        default="_",
        help="Separator used to split key prefix (default: '_').",
    )
    parser.add_argument(
        "--min-prefix-length",
        type=int,
        default=2,
        metavar="N",
        help="Minimum prefix length to form a group (default: 2).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_pivot_command)


def run_pivot_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = pivot_config(
        config,
        separator=args.separator,
        min_prefix_length=args.min_prefix_length,
    )

    if args.format == "json":
        payload = {
            "summary": result.summary(),
            "group_count": result.group_count,
            "original_count": result.original_count,
            "groups": result.pivoted,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        for group, keys in result.pivoted.items():
            print(f"\n[{group}]")
            for sub_key, value in keys.items():
                print(f"  {sub_key}={value}")

    return 0
