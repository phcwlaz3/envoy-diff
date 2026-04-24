"""CLI command: envoy-diff stack — overlay multiple env files into a merged view."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.stacker import stack_configs


def add_stack_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "stack",
        help="Overlay multiple env files and show the effective merged config.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more env/JSON files in layer order (later files win by default).",
    )
    parser.add_argument(
        "--strategy",
        choices=["last-wins", "first-wins"],
        default="last-wins",
        help="Merge strategy (default: last-wins).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all layer values for each key, not just the effective one.",
    )
    parser.set_defaults(func=run_stack_command)


def run_stack_command(args: argparse.Namespace) -> int:
    layers = []
    for path in args.files:
        try:
            layers.append(load_config(path))
        except Exception as exc:  # noqa: BLE001
            print(f"error: cannot load '{path}': {exc}", file=sys.stderr)
            return 1

    result = stack_configs(layers, strategy=args.strategy)

    if args.fmt == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        _render_text(result, show_all=args.show_all, layer_names=args.files)

    return 0


def _render_text(result, *, show_all: bool, layer_names: List[str]) -> None:
    print(f"Layers : {result.layer_count}")
    for i, name in enumerate(layer_names):
        print(f"  [{i}] {name}")
    print(f"Keys   : {len(result.entries)}")
    print(f"Overridden: {result.override_count}")
    print()
    for key, entry in sorted(result.entries.items()):
        marker = "*" if len(entry.all_values) > 1 else " "
        print(f"{marker} {key}={entry.effective_value}  (layer {entry.source_index})")
        if show_all and len(entry.all_values) > 1:
            for idx, val in entry.all_values:
                print(f"      [{idx}] {val}")
