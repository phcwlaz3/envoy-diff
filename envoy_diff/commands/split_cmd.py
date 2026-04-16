"""CLI sub-command: split a config file into prefix-based buckets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_diff.loader import load_config
from envoy_diff.splitter import split_config


def add_split_subparsers(subparsers) -> None:
    p = subparsers.add_parser("split", help="Split config keys by prefix")
    p.add_argument("file", help="Path to .env or .json config file")
    p.add_argument(
        "--prefix",
        dest="prefixes",
        action="append",
        default=[],
        metavar="PREFIX",
        help="Prefix to split on (repeatable); omit for auto-detect",
    )
    p.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect prefixes from key names",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    p.set_defaults(func=run_split_command)


def run_split_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    prefixes = args.prefixes or None
    result = split_config(config, prefixes=prefixes, auto=args.auto)

    if args.format == "json":
        out = {
            "buckets": result.buckets,
            "unmatched": result.unmatched,
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        for bucket, keys in result.buckets.items():
            print(f"[{bucket}]")
            for k, v in keys.items():
                print(f"  {k}={v}")
        if result.unmatched:
            print("[unmatched]")
            for k, v in result.unmatched.items():
                print(f"  {k}={v}")
        print(result.summary())

    return 0
