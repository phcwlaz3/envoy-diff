"""CLI sub-command: render a template file using an env config."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_diff.loader import load_config
from envoy_diff.templater import render_template


def add_template_subparsers(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="Render a template using env config values")
    p.add_argument("template_file", help="Path to template file containing {{ KEY }} placeholders")
    p.add_argument("config_file", help="Env or JSON config file supplying values")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )
    p.add_argument("--output", "-o", default="-", help="Output file path (default: stdout)")
    p.add_argument(
        "--strict", action="store_true", help="Exit with error code 1 if any placeholders are unresolved"
    )


def run_template_command(args: argparse.Namespace) -> int:
    try:
        template_text = Path(args.template_file).read_text()
    except OSError as exc:
        print(f"error: cannot read template file: {exc}", file=sys.stderr)
        return 1

    try:
        config = load_config(args.config_file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot load config: {exc}", file=sys.stderr)
        return 1

    result = render_template(template_text, config)

    if args.format == "json":
        payload = json.dumps(
            {
                "rendered": result.rendered,
                "resolved_keys": result.resolved_keys,
                "unresolved_keys": result.unresolved_keys,
                "summary": result.summary(),
            },
            indent=2,
        )
        output = payload
    else:
        output = result.rendered

    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output)

    if args.strict and result.has_unresolved:
        print(
            f"error: {len(result.unresolved_keys)} unresolved placeholder(s): "
            f"{', '.join(result.unresolved_keys)}",
            file=sys.stderr,
        )
        return 1

    return 0
