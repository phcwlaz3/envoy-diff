from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.prefixer import add_prefix, remove_prefix


def add_prefix_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "prefix",
        help="Add or remove a prefix from environment variable keys",
    )
    parser.add_argument("file", help="Path to the env or JSON config file")
    parser.add_argument("--prefix", required=True, help="Prefix string to add or remove")
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--add",
        dest="action",
        action="store_const",
        const="add",
        default="add",
        help="Add the prefix to all keys (default)",
    )
    action_group.add_argument(
        "--remove",
        dest="action",
        action="store_const",
        const="remove",
        help="Remove the prefix from matching keys",
    )
    parser.add_argument(
        "--skip-prefixed",
        action="store_true",
        default=False,
        help="Skip keys that already have the prefix (add mode only)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )


def run_prefix_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    if args.action == "remove":
        result = remove_prefix(config, args.prefix)
    else:
        result = add_prefix(config, args.prefix, skip_already_prefixed=args.skip_prefixed)

    if args.format == "json":
        print(json.dumps({
            "config": result.config,
            "changes": result.changed,
            "change_count": result.change_count(),
            "summary": result.summary(),
        }, indent=2))
    else:
        print(result.summary())
        for original, updated in result.changes.items():
            print(f"  {original!r} -> {updated!r}")

    return 0
