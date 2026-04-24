"""CLI subcommand: envoy-diff zip — zip two env files side-by-side."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.zipper import ZipResult, zip_configs


def add_zip_subparsers(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "zip",
        help="Zip two env config files by key for side-by-side comparison.",
    )
    parser.add_argument("left", help="Left / base config file")
    parser.add_argument("right", help="Right / head config file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    parser.add_argument(
        "--no-sort",
        action="store_true",
        default=False,
        help="Preserve key order instead of sorting alphabetically.",
    )
    parser.add_argument(
        "--diff-only",
        action="store_true",
        default=False,
        help="Only show rows where values differ or a key is missing.",
    )
    parser.set_defaults(func=run_zip_command)


def run_zip_command(args: argparse.Namespace) -> int:
    try:
        left = load_config(args.left)
        right = load_config(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading configs: {exc}", file=sys.stderr)
        return 1

    result = zip_configs(left, right, sort=not args.no_sort)

    if args.fmt == "json":
        _render_json(result, diff_only=args.diff_only)
    else:
        _render_text(result, diff_only=args.diff_only)

    return 0


def _render_text(result: ZipResult, diff_only: bool = False) -> None:
    rows = result.rows if not diff_only else [
        r for r in result.rows if not r.is_equal
    ]
    col = 30
    print(f"{'KEY':<{col}}  {'LEFT':<{col}}  {'RIGHT':<{col}}")
    print("-" * (col * 3 + 4))
    for row in rows:
        marker = "~" if row.is_aligned and not row.is_equal else ("+" if row.left is None else ("-" if row.right is None else " "))
        lv = row.left or "<missing>"
        rv = row.right or "<missing>"
        print(f"{marker} {row.key:<{col}}  {lv:<{col}}  {rv:<{col}}")
    print()
    print(result.summary())


def _render_json(result: ZipResult, diff_only: bool = False) -> None:
    rows = result.rows if not diff_only else [
        r for r in result.rows if not r.is_equal
    ]
    payload = {
        "summary": result.summary(),
        "left_only": result.left_only,
        "right_only": result.right_only,
        "aligned_count": result.aligned_count(),
        "diff_count": result.diff_count(),
        "rows": [
            {"key": r.key, "left": r.left, "right": r.right, "equal": r.is_equal}
            for r in rows
        ],
    }
    print(json.dumps(payload, indent=2))
