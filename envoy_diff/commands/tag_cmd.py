"""CLI sub-command: tag — label config keys using pattern rules."""
import json
import argparse
from typing import Optional

from envoy_diff.loader import load_config
from envoy_diff.tagger import tag_config

_DEFAULT_RULES = {
    "secret": ["PASSWORD", "SECRET", "TOKEN", "KEY", "PRIVATE"],
    "database": ["DB", "DATABASE", "POSTGRES", "MYSQL", "REDIS"],
    "feature": ["FEATURE", "FLAG", "ENABLE", "DISABLE"],
    "network": ["HOST", "PORT", "URL", "ENDPOINT", "ADDR"],
}


def add_tag_subparsers(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Tag config keys with labels")
    p.add_argument("file", help="Path to env or JSON config file")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    p.add_argument(
        "--rules", help="Path to JSON file with custom tag rules", default=None
    )


def run_tag_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}")
        return 1

    rules = _DEFAULT_RULES
    if args.rules:
        try:
            with open(args.rules) as fh:
                rules = json.load(fh)
        except Exception as exc:
            print(f"Error loading rules file: {exc}")
            return 1

    result = tag_config(config, rules)

    if args.fmt == "json":
        output = {
            "tagged": {k: v for k, v in result.tagged.items()},
            "untagged": sorted(result.untagged),
            "tag_count": result.tag_count(),
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.tagged:
            print("\nTagged keys:")
            for key, tags in sorted(result.tagged.items()):
                print(f"  {key}: {', '.join(tags)}")
        if result.untagged:
            print("\nUntagged keys:")
            for key in sorted(result.untagged):
                print(f"  {key}")

    return 0
