"""CLI subcommand for comparing two environment config files."""

from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config, UnsupportedFormatError
from envoy_diff.comparator import compare_configs


def add_compare_subparsers(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'compare' subcommand."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two environment config files and report differences.",
    )
    parser.add_argument("base", help="Path to the base config file (.env or .json).")
    parser.add_argument("target", help="Path to the target config file (.env or .json).")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        default=False,
        help="Exit with non-zero status if differences are found.",
    )
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged keys in the output.",
    )
    parser.set_defaults(func=run_compare_command)


def run_compare_command(args: argparse.Namespace) -> int:
    """Execute the compare subcommand.

    Returns an exit code (0 = success / no diff, 1 = diff found or error).
    """
    # Load both configs
    try:
        base_config = load_config(args.base)
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"Error loading base file: {exc}", file=sys.stderr)
        return 1

    try:
        target_config = load_config(args.target)
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"Error loading target file: {exc}", file=sys.stderr)
        return 1

    result = compare_configs(base_config, target_config)

    if args.format == "json":
        _render_json(result, show_unchanged=args.show_unchanged)
    else:
        _render_text(result, show_unchanged=args.show_unchanged)

    if args.fail_on_diff and result.has_diff():
        return 1
    return 0


def _render_text(result, *, show_unchanged: bool) -> None:
    """Print a human-readable comparison report."""
    print(result.summary())

    if result.added:
        print("\nAdded keys:")
        for key, val in sorted(result.added.items()):
            print(f"  + {key}={val}")

    if result.removed:
        print("\nRemoved keys:")
        for key, val in sorted(result.removed.items()):
            print(f"  - {key}={val}")

    if result.changed:
        print("\nChanged keys:")
        for key, (old, new) in sorted(result.changed.items()):
            print(f"  ~ {key}: {old!r} -> {new!r}")

    if show_unchanged and result.unchanged:
        print("\nUnchanged keys:")
        for key, val in sorted(result.unchanged.items()):
            print(f"    {key}={val}")


def _render_json(result, *, show_unchanged: bool) -> None:
    """Print a JSON comparison report."""
    data: dict = {
        "summary": result.summary(),
        "has_diff": result.has_diff(),
        "added": result.added,
        "removed": result.removed,
        "changed": {
            k: {"old": old, "new": new}
            for k, (old, new) in result.changed.items()
        },
    }
    if show_unchanged:
        data["unchanged"] = result.unchanged
    print(json.dumps(data, indent=2))
