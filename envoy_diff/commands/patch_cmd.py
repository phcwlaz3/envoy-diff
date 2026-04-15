"""CLI sub-command: envoy-diff patch.

Apply a JSON diff file onto a base env config and print the result.

Usage examples
--------------
    envoy-diff patch base.env diff.json
    envoy-diff patch base.env diff.json --strict
    envoy-diff patch base.env diff.json --ignore-removed --format json
"""

import argparse
import json
import sys
from typing import List

from envoy_diff.differ import DiffResult
from envoy_diff.loader import load_config
from envoy_diff.patcher import PatchError, patch_config


def add_patch_subparsers(subparsers) -> None:  # noqa: ANN001
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "patch",
        help="Apply a diff file onto a base env config",
    )
    parser.add_argument("base", help="Base env/JSON config file")
    parser.add_argument("diff_file", help="JSON diff file produced by envoy-diff")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Abort on any conflict instead of recording errors",
    )
    parser.add_argument(
        "--ignore-removed",
        action="store_true",
        default=False,
        help="Skip removal operations instead of applying them",
    )
    parser.add_argument(
        "--format",
        choices=["env", "json"],
        default="env",
        help="Output format (default: env)",
    )
    parser.set_defaults(func=run_patch_command)


def run_patch_command(args: argparse.Namespace) -> int:
    # Load base config
    try:
        base = load_config(args.base)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading base config: {exc}", file=sys.stderr)
        return 1

    # Load diff JSON
    try:
        with open(args.diff_file, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        diff = DiffResult(
            added=raw.get("added", {}),
            removed=raw.get("removed", {}),
            changed={k: tuple(v) for k, v in raw.get("changed", {}).items()},
            unchanged=raw.get("unchanged", {}),
        )
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Error loading diff file: {exc}", file=sys.stderr)
        return 1

    # Apply patch
    try:
        result = patch_config(
            base,
            diff,
            strict=args.strict,
            ignore_removed=args.ignore_removed,
        )
    except PatchError as exc:
        print(f"Patch failed: {exc}", file=sys.stderr)
        return 2

    # Report errors (non-strict mode)
    if result.has_errors:
        for err in result.errors:
            print(f"WARNING: {err}", file=sys.stderr)

    # Output patched config
    if args.format == "json":
        print(json.dumps(result.patched, indent=2))
    else:
        for key, value in sorted(result.patched.items()):
            print(f"{key}={value}")

    print(f"\n# {result.summary()}", file=sys.stderr)
    return 1 if result.has_errors else 0
