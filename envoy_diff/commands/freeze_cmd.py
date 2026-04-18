"""CLI subcommands for freeze/drift detection."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.freezer import check_drift, freeze_config
from envoy_diff.loader import load_config


def add_freeze_subparsers(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("freeze", help="Freeze and drift-check env configs")
    sub = p.add_subparsers(dest="freeze_cmd", required=True)

    check_p = sub.add_parser("check", help="Check live config against a frozen baseline")
    check_p.add_argument("baseline", help="Baseline (frozen) env file")
    check_p.add_argument("live", help="Live env file to compare")
    check_p.add_argument("--ignore", nargs="*", default=[], metavar="KEY", help="Keys to ignore")
    check_p.add_argument("--format", choices=["text", "json"], default="text")

    dump_p = sub.add_parser("dump", help="Print a frozen copy of a config")
    dump_p.add_argument("file", help="Env file to freeze")
    dump_p.add_argument("--format", choices=["text", "json"], default="json")


def run_freeze_command(args: argparse.Namespace) -> int:
    if args.freeze_cmd == "check":
        return _cmd_check(args)
    if args.freeze_cmd == "dump":
        return _cmd_dump(args)
    return 1


def _cmd_check(args: argparse.Namespace) -> int:
    try:
        baseline = load_config(args.baseline)
        live = load_config(args.live)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    result = check_drift(baseline, live, ignore_keys=args.ignore)

    if args.format == "json":
        print(json.dumps({
            "has_drift": result.has_drift,
            "drift_count": result.drift_count,
            "drifted": result.drifted,
            "added": result.added,
            "removed": result.removed,
            "summary": result.summary(),
        }, indent=2))
    else:
        print(result.summary())
        if result.drifted:
            print("  Changed:", ", ".join(result.drifted))
        if result.added:
            print("  Added:  ", ", ".join(result.added))
        if result.removed:
            print("  Removed:", ", ".join(result.removed))

    return 1 if result.has_drift else 0


def _cmd_dump(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    frozen = freeze_config(config)

    if args.format == "json":
        print(json.dumps(frozen, indent=2))
    else:
        for k, v in frozen.items():
            print(f"{k}={v}")

    return 0
