"""CLI sub-command: version — stamp a config file with version metadata."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.versioner import version_config


def add_version_subparsers(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "version",
        help="Stamp a config file with version metadata.",
    )
    parser.add_argument("file", help="Path to .env or .json config file.")
    parser.add_argument("version", help="Version string to stamp (e.g. 1.2.3).")
    parser.add_argument("--label", default=None, help="Optional release label.")
    parser.add_argument(
        "--prefix",
        default="ENVOY_",
        help="Key prefix for injected metadata (default: ENVOY_).",
    )
    parser.add_argument(
        "--no-inject",
        action="store_true",
        help="Do not inject metadata keys; only record version in result.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.set_defaults(func=run_version_command)


def run_version_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = version_config(
        config,
        version=args.version,
        label=args.label,
        prefix=args.prefix,
        inject_keys=not args.no_inject,
    )

    if args.format == "json":
        out = {
            "version": result.version,
            "stamped_at": result.stamped_at,
            "label": result.label,
            "stamp_count": result.stamp_count(),
            "keys_stamped": result.keys_stamped,
            "config": result.config,
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        if result.has_stamps():
            print("Stamped keys:")
            for key in result.keys_stamped:
                print(f"  + {key} = {result.config[key]}")

    return 0
