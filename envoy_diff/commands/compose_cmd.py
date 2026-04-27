"""CLI sub-command: compose multiple env files into one config."""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from envoy_diff.composer import compose_configs
from envoy_diff.loader import load_config


def add_compose_subparsers(subparsers) -> None:  # type: ignore[type-arg]
    parser: ArgumentParser = subparsers.add_parser(
        "compose",
        help="Compose multiple env/json files into a single config.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more env/json files to compose (name=path or plain path).",
    )
    parser.add_argument(
        "--order",
        nargs="*",
        metavar="NAME",
        help="Explicit fragment merge order (by name).",
    )
    parser.add_argument(
        "--on-conflict",
        choices=["last_wins", "first_wins"],
        default="last_wins",
        dest="on_conflict",
        help="Conflict resolution strategy (default: last_wins).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_compose_command)


def run_compose_command(args: Namespace) -> int:
    fragments = {}
    for entry in args.files:
        if "=" in entry:
            name, path = entry.split("=", 1)
        else:
            name = entry
            path = entry
        try:
            fragments[name] = load_config(path)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not load '{path}': {exc}", file=sys.stderr)
            return 1

    result = compose_configs(
        fragments,
        order=args.order or None,
        on_conflict=args.on_conflict,
    )

    if args.format == "json":
        output = {
            "config": result.config,
            "fragments_used": result.fragments_used,
            "skipped_fragments": result.skipped_fragments,
            "conflicts": result.conflicts,
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"# composed config  —  {result.summary()}")
        if result.conflicts:
            print(f"# conflicts ({args.on_conflict}): {', '.join(result.conflicts)}")
        for key, value in sorted(result.config.items()):
            print(f"{key}={value}")

    return 0
