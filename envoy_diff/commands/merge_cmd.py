"""CLI sub-command: merge multiple env files into one."""

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import List

from envoy_diff.loader import load_config
from envoy_diff.merger import merge_configs


def add_merge_subparsers(subparsers: _SubParsersAction) -> None:
    parser: ArgumentParser = subparsers.add_parser(
        "merge",
        help="Merge multiple env/json config files into a single output.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more config files to merge.",
    )
    parser.add_argument(
        "--strategy",
        choices=["last_wins", "first_wins"],
        default="last_wins",
        help="Conflict resolution strategy (default: last_wins).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--fail-on-conflict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any conflicts are detected.",
    )
    parser.set_defaults(func=run_merge_command)


def run_merge_command(args: Namespace) -> int:
    configs = []
    sources: List[str] = []

    for path in args.files:
        try:
            cfg = load_config(path)
            configs.append(cfg)
            sources.append(path)
        except Exception as exc:  # noqa: BLE001
            print(f"Error loading {path!r}: {exc}", file=sys.stderr)
            return 1

    result = merge_configs(configs, sources=sources, strategy=args.strategy)

    if args.output_format == "json":
        output = {
            "merged": result.merged,
            "conflicts": result.conflicts,
            "sources": result.sources,
            "summary": result.summary(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if result.has_conflicts():
            print("\nConflicts detected:")
            for key, values in result.conflicts.items():
                print(f"  {key}: {' | '.join(values)}")
        else:
            print("\nMerged config:")
            for key, value in sorted(result.merged.items()):
                print(f"  {key}={value}")

    if args.fail_on_conflict and result.has_conflicts():
        return 1
    return 0
