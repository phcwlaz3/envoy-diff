from __future__ import annotations
import argparse
import json
import sys
from envoy_diff.loader import load_config
from envoy_diff.extractor import extract_config


def add_extract_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("extract", help="Extract a subset of keys from a config file")
    parser.add_argument("file", help="Path to the env or JSON config file")
    parser.add_argument("--keys", nargs="+", metavar="KEY", help="Explicit keys to extract")
    parser.add_argument("--pattern", metavar="REGEX", help="Regex pattern to match keys")
    parser.add_argument("--prefix", metavar="PREFIX", help="Key prefix to extract")
    parser.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    parser.add_argument("--show-skipped", action="store_true", help="Also list skipped keys")


def run_extract_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = extract_config(
        config,
        keys=args.keys,
        pattern=args.pattern,
        prefix=args.prefix,
    )

    if args.fmt == "json":
        out = {
            "extracted": result.extracted,
            "extract_count": result.extract_count(),
            "skipped": result.skipped if args.show_skipped else [],
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Extracted {result.extract_count()} key(s) — {result.summary()}")
        for key, value in result.extracted.items():
            print(f"  {key}={value}")
        if args.show_skipped and result.skipped:
            print(f"\nSkipped ({len(result.skipped)}):")
            for key in result.skipped:
                print(f"  {key}")

    return 0
