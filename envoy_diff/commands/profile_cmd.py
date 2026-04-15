"""CLI sub-command: profile — score and analyse an environment config file."""

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.profiler import profile_config


def add_profile_subparsers(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "profile",
        help="Score and analyse an environment config file.",
    )
    parser.add_argument("file", help="Path to the .env or .json config file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_profile_command)


def run_profile_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = profile_config(config)

    if args.format == "json":
        payload = {
            "file": args.file,
            "score": result.score,
            "grade": result.grade(),
            "total_keys": result.total_keys,
            "empty_count": result.empty_count,
            "suspicious_keys": result.suspicious_keys,
            "notes": result.notes,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Profile: {args.file}")
        print(f"  Score : {result.score}/100  (Grade: {result.grade()})")
        print(f"  Keys  : {result.total_keys} total, {result.empty_count} empty")
        if result.suspicious_keys:
            print(f"  Suspicious keys: {', '.join(result.suspicious_keys)}")
        for note in result.notes:
            print(f"  ⚠  {note}")

    return 0
