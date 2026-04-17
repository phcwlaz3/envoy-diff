"""CLI sub-command: scope — filter config keys by deployment scope."""
from __future__ import annotations
import argparse
import json
import sys
from envoy_diff.loader import load_config
from envoy_diff.scoper import scope_config, BUILTIN_SCOPES


def add_scope_subparsers(subparsers) -> None:
    p = subparsers.add_parser("scope", help="Filter config keys by named scope")
    p.add_argument("file", help="Path to .env or .json config file")
    p.add_argument("scope", help=f"Scope name. Builtin: {', '.join(BUILTIN_SCOPES)}")
    p.add_argument(
        "--prefix",
        action="append",
        dest="extra_prefixes",
        metavar="PREFIX",
        help="Extra key prefix to include (repeatable)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--show-excluded",
        action="store_true",
        help="Also print excluded keys",
    )


def run_scope_command(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading file: {exc}", file=sys.stderr)
        return 1

    result = scope_config(config, args.scope, extra_prefixes=args.extra_prefixes)

    if args.format == "json":
        out = {
            "scope": result.scope,
            "matched": result.matched,
            "matched_count": result.matched_count(),
            "excluded_count": result.excluded_count(),
        }
        if args.show_excluded:
            out["excluded"] = result.excluded
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        print()
        if result.matched:
            print("Matched keys:")
            for k, v in result.matched.items():
                print(f"  {k}={v}")
        else:
            print("  (no keys matched)")
        if args.show_excluded and result.excluded:
            print()
            print("Excluded keys:")
            for k, v in result.excluded.items():
                print(f"  {k}={v}")

    return 0
