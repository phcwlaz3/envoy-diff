from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.summarizer import summarize_config


def add_summarize_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "summarize",
        help="Summarize key statistics of an env config file",
    )
    parser.add_argument("file", help="Path to env or JSON config file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.set_defaults(func=run_summarize_command)


def _format_text_output(result) -> str:
    """Format a SummaryResult as human-readable text.

    Returns a multi-line string with the summary header followed by
    individual statistics for total keys, unique values, empty values,
    and duplicate groups.
    """
    lines = [
        result.summary(),
        f"  Total keys       : {result.total_keys}",
        f"  Unique values    : {result.unique_values}",
        f"  Empty values     : {result.empty_count}",
        f"  Duplicate groups : {result.duplicate_group_count}",
    ]
    return "\n".join(lines)


def run_summarize_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = summarize_config(config)

    if args.fmt == "json":
        out = {
            "total_keys": result.total_keys,
            "unique_values": result.unique_values,
            "empty_count": result.empty_count,
            "duplicate_group_count": result.duplicate_group_count,
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        print(_format_text_output(result))

    return 0
