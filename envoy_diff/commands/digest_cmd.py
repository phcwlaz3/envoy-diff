"""CLI subcommand: digest — hash an env config and optionally detect drift."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.digester import digest_config
from envoy_diff.loader import load_config


def add_digest_subparsers(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("digest", help="Compute a hash digest of an env config file")
    p.add_argument("file", help="Path to .env or .json config file")
    p.add_argument(
        "--algorithm", "-a", default="sha256",
        help="Hash algorithm to use (default: sha256)",
    )
    p.add_argument(
        "--compare", "-c", metavar="PREVIOUS_DIGEST",
        help="Previous digest to compare against for drift detection",
    )
    p.add_argument(
        "--format", "-f", choices=["text", "json"], default="text",
        dest="output_format",
    )
    p.set_defaults(func=run_digest_command)


def run_digest_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    try:
        result = digest_config(
            config,
            algorithm=args.algorithm,
            previous_digest=getattr(args, "compare", None),
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == "json":
        out = {
            "digest": result.digest,
            "algorithm": result.algorithm,
            "key_count": result.key_count,
            "changed": result.changed,
            "previous_digest": result.previous_digest,
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        if result.changed:
            print("  Drift detected — config has changed since last digest.")

    return 1 if result.changed else 0
