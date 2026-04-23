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


def _load_rules(rules_path: str) -> dict:
    """Load tag rules from a JSON file, validating basic structure."""
    with open(rules_path) as fh:
        rules = json.load(fh)
    if not isinstance(rules, dict):
        raise ValueError("Rules file must contain a JSON object at the top level")
    for tag, patterns in rules.items():
        if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
            raise ValueError(f"Patterns for tag '{tag}' must be a list of strings")
    return rules


def _merge_rules(base: dict, override: dict) -> dict:
    """Merge override rules into base rules, combining pattern lists per tag.

    Tags present in both dicts have their pattern lists unioned (duplicates
    removed).  Tags exclusive to either dict are included as-is.

    Args:
        base: The default or existing rule set.
        override: Rules loaded from a user-supplied file.

    Returns:
        A new dict with merged tag-to-patterns mappings.
    """
    merged = {tag: list(patterns) for tag, patterns in base.items()}
    for tag, patterns in override.items():
        if tag in merged:
            merged[tag] = list(dict.fromkeys(merged[tag] + patterns))
        else:
            merged[tag] = list(patterns)
    return merged


def add_tag_subparsers(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Tag config keys with labels")
    p.add_argument("file", help="Path to env or JSON config file")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    p.add_argument(
        "--rules", help="Path to JSON file with custom tag rules", default=None
    )
    p.add_argument(
        "--merge-rules",
        help="Merge custom rules with built-in defaults instead of replacing them",
        action="store_true",
        default=False,
        dest="merge_rules",
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
            custom_rules = _load_rules(args.rules)
        except Exception as exc:
            print(f"Error loading rules file: {exc}")
            return 1
        rules = _merge_rules(_DEFAULT_RULES, custom_rules) if args.merge_rules else custom_rules

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
