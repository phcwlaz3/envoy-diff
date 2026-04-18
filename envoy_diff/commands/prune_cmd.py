"""CLI sub-command: prune — remove keys from a config file."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.pruner import prune_config


def add_prune_subparsers(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "prune", help="Remove keys from a config file by name or pattern."
    )
    parser.add_argument("file", help="Path to the env/JSON config file.")
    parser.add_argument(
        "--key",
        dest="keys",
        action="append",
        default=[],
        metavar="KEY",
        help="Exact key to remove (repeatable).",
    )
    parser.add_argument(
        "--pattern",
        dest="patterns",
        action="append",
        default=[],
        metavar="PATTERN",
        help="fnmatch pattern for keys to remove (repeatable).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_prune_command)


def run_prune_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = prune_config(config, keys=args.keys, patterns=args.patterns)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pruned": result.pruned,
                    "removed_keys": sorted(result.removed_keys),
                    "removed_count": result.removed_count(),
                    "summary": result.summary(),
                },
                indent=2,
            )
        )
    else:
        print(result.summary())
        if result.has_removals():
            print("\nRemaining config:")
            for k, v in sorted(result.pruned.items()):
                print(f"  {k}={v}")

    return 0
