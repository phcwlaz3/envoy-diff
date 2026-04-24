"""CLI sub-command: map — remap environment variable keys to a new schema."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.mapper import map_config


def add_map_subparsers(subparsers) -> None:  # type: ignore[type-arg]
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "map",
        help="Remap environment variable keys using explicit mappings or regex patterns.",
    )
    parser.add_argument("file", help="Path to the env/JSON config file.")
    parser.add_argument(
        "--map",
        metavar="OLD=NEW",
        action="append",
        default=[],
        dest="mappings",
        help="Explicit key mapping (repeatable). E.g. --map DB_HOST=DATABASE_HOST",
    )
    parser.add_argument(
        "--pattern",
        metavar="REGEX=REPLACEMENT",
        action="append",
        default=[],
        dest="patterns",
        help="Regex pattern mapping (repeatable). E.g. --pattern '^DB_=DATABASE_'",
    )
    parser.add_argument(
        "--drop-unmapped",
        action="store_true",
        default=False,
        help="Exclude keys that have no mapping from the output.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.set_defaults(func=run_map_command)


def _parse_pairs(items: List[str], flag: str) -> dict:
    result = {}
    for item in items:
        if "=" not in item:
            print(f"error: invalid {flag} value '{item}' — expected KEY=VALUE", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        result[k] = v
    return result


def run_map_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    explicit = _parse_pairs(args.mappings, "--map")
    patterns = _parse_pairs(args.patterns, "--pattern")

    result = map_config(
        config,
        explicit=explicit,
        patterns=patterns,
        drop_unmapped=args.drop_unmapped,
    )

    if args.format == "json":
        output = {
            "mapped": result.mapped,
            "mapping_applied": result.mapping_applied,
            "unmapped": result.unmapped,
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"# {result.summary()}")
        for key, value in result.mapped.items():
            marker = "~" if key in result.mapping_applied or any(
                new == key for new in [explicit.get(old) for old in result.mapping_applied]
            ) else " "
            print(f"  {key}={value}")
        if result.unmapped:
            print(f"\nunmapped keys ({len(result.unmapped)}): {', '.join(result.unmapped)}")

    return 0
