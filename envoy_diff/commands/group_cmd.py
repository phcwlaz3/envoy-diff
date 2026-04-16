"""CLI sub-command: group — display env vars grouped by prefix."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.grouper import group_config


def add_group_subparsers(subparsers) -> None:
    p = subparsers.add_parser("group", help="Group env vars by prefix")
    p.add_argument("file", help="Env or JSON config file")
    p.add_argument(
        "--prefix", dest="prefixes", action="append", default=[],
        metavar="PREFIX", help="Explicit prefix to group by (repeatable)"
    )
    p.add_argument(
        "--no-auto", dest="auto_detect", action="store_false", default=True,
        help="Disable auto-detection of prefixes"
    )
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format"
    )
    p.set_defaults(func=run_group_command)


def run_group_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = group_config(
        config,
        prefixes=args.prefixes or None,
        auto_detect=args.auto_detect,
    )

    if args.format == "json":
        out = {
            "groups": result.groups,
            "ungrouped": result.ungrouped,
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        for name, keys in result.groups.items():
            print(f"[{name}]")
            for k, v in sorted(keys.items()):
                print(f"  {k}={v}")
        if result.ungrouped:
            print("[ungrouped]")
            for k, v in sorted(result.ungrouped.items()):
                print(f"  {k}={v}")
        print(result.summary())

    return 0
