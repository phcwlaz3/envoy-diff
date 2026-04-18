"""CLI command for diffing two env config files."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.loader import load_config
from envoy_diff.differ import diff_configs
from envoy_diff.scorer import score_diff


def add_diff_subparsers(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("diff", help="Diff two environment config files")
    p.add_argument("base", help="Base config file")
    p.add_argument("head", help="Head config file")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--score", action="store_true", help="Include risk score")
    p.set_defaults(func=run_diff_command)


def run_diff_command(args: argparse.Namespace) -> int:
    try:
        base = load_config(args.base)
        head = load_config(args.head)
    except Exception as exc:
        print(f"Error loading files: {exc}", file=sys.stderr)
        return 1

    result = diff_configs(base, head)

    if args.format == "json":
        data = {
            "added": result.added,
            "removed": result.removed,
            "changed": {k: {"old": v[0], "new": v[1]} for k, v in result.changed.items()},
            "unchanged_count": len(result.unchanged),
            "has_diff": result.has_diff(),
        }
        if args.score:
            sr = score_diff(result)
            data["score"] = sr.score
            data["risk"] = sr.risk_level
        print(json.dumps(data, indent=2))
    else:
        _render_text(result)
        if args.score:
            sr = score_diff(result)
            print(f"\nRisk score: {sr.score}/100  ({sr.risk_level} risk)")

    return 1 if result.has_diff() else 0


def _render_text(result) -> None:
    if not result.has_diff():
        print("No differences found.")
        return
    for k, v in result.added.items():
        print(f"+ {k}={v}")
    for k in result.removed:
        print(f"- {k}")
    for k, (old, new) in result.changed.items():
        print(f"~ {k}: {old!r} -> {new!r}")
