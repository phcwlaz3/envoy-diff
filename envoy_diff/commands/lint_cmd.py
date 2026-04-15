"""CLI sub-command: lint — check env config for naming/style issues."""

import argparse
import json
import sys
from envoy_diff.loader import load_config
from envoy_diff.linter import lint_config


def add_lint_subparsers(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("lint", help="Lint an env config file for style issues")
    parser.add_argument("file", help="Path to .env or .json config file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if any warnings exist",
    )


def run_lint_command(args: argparse.Namespace) -> int:
    """Execute the lint command. Returns exit code."""
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = lint_config(config)

    if args.format == "json":
        output = {
            "summary": result.summary(),
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "issues": [
                {"key": i.key, "message": i.message, "severity": i.severity}
                for i in result.issues
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        for issue in result.issues:
            print(f"  [{issue.severity.upper()}] {issue.key}: {issue.message}")

    if result.error_count > 0:
        return 2
    if args.strict and result.warning_count > 0:
        return 1
    return 0
