from __future__ import annotations
import argparse
import json
from envoy_diff.loader import load_config
from envoy_diff.expander import expand_config


def add_expand_subparsers(subparsers) -> None:
    parser = subparsers.add_parser("expand", help="Expand multi-value keys into indexed sub-keys")
    parser.add_argument("file", help="Env or JSON config file")
    parser.add_argument("--delimiter", default=",", help="Value delimiter (default: comma)")
    parser.add_argument(
        "--suffix", default="_{i}", dest="suffix_template",
        help="Suffix template for new keys, use {i} as index placeholder (default: _{i})"
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")


def run_expand_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}")
        return 1

    result = expand_config(
        config,
        delimiter=args.delimiter,
        suffix_template=args.suffix_template,
    )

    if args.format == "json":
        print(json.dumps({
            "config": result.config,
            "expanded": result.expanded,
            "expand_count": result.expand_count,
            "summary": result.summary(),
        }, indent=2))
    else:
        print(result.summary())
        for key, value in sorted(result.config.items()):
            print(f"  {key}={value}")

    return 0
