"""CLI sub-command: redact sensitive values from an env config file."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from envoy_diff.loader import load_config
from envoy_diff.redactor import DEFAULT_MASK, redact_config


def add_redact_subparsers(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser("redact", help="Mask sensitive values in a config file")
    parser.add_argument("file", help="Path to the env/JSON config file")
    parser.add_argument(
        "--mask",
        default=DEFAULT_MASK,
        help="Replacement string for sensitive values (default: ***REDACTED***)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format",
    )
    parser.add_argument(
        "--show-summary",
        action="store_true",
        help="Print redaction summary to stderr",
    )


def run_redact_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = redact_config(config, mask=args.mask)

    if args.show_summary:
        print(result.summary(), file=sys.stderr)

    if args.output_format == "json":
        print(json.dumps(result.redacted, indent=2))
    else:
        for key, value in sorted(result.redacted.items()):
            print(f"{key}={value}")

    return 0
