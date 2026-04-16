"""CLI subcommands for pinning and drift-checking env configs."""

from __future__ import annotations

import json
import argparse
from envoy_diff.loader import load_config
from envoy_diff.pinner import pin_config, check_drift
from envoy_diff.snapshotter import save_snapshot, load_snapshot


def add_pin_subparsers(subparsers) -> None:
    pin_parser = subparsers.add_parser("pin", help="Pin and drift-check env configs")
    pin_sub = pin_parser.add_subparsers(dest="pin_cmd")

    save_p = pin_sub.add_parser("save", help="Pin current config values")
    save_p.add_argument("file", help="Env file to pin")
    save_p.add_argument("--keys", nargs="+", help="Keys to pin (default: all)")
    save_p.add_argument("--output-dir", default=".envoy_pins", help="Directory for pins")
    save_p.add_argument("--label", default=None, help="Label for the pin snapshot")

    check_p = pin_sub.add_parser("check", help="Check config drift against pins")
    check_p.add_argument("file", help="Current env file")
    check_p.add_argument("snapshot", help="Path to pinned snapshot file")
    check_p.add_argument("--format", choices=["text", "json"], default="text")


def run_pin_command(args: argparse.Namespace) -> int:
    if args.pin_cmd == "save":
        return _cmd_save(args)
    if args.pin_cmd == "check":
        return _cmd_check(args)
    print("No pin subcommand given. Use 'save' or 'check'.")
    return 1


def _cmd_save(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
    except Exception as exc:
        print(f"Error loading file: {exc}")
        return 1

    result = pin_config(config, keys=args.keys)
    if result.unpinned:
        print(f"Warning: keys not found: {', '.join(result.unpinned)}")

    try:
        path = save_snapshot(result.pinned, output_dir=args.output_dir, label=args.label)
        print(f"Pinned {result.pin_count} keys to {path}")
    except Exception as exc:
        print(f"Error saving pin: {exc}")
        return 1
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.file)
        pins = load_snapshot(args.snapshot)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    result = check_drift(config, pins)

    if args.format == "json":
        print(json.dumps({
            "has_drift": result.has_drift(),
            "drift_count": result.drift_count,
            "drifted": {k: {"pinned": v[0], "current": v[1]} for k, v in result.drifted.items()},
        }, indent=2))
    else:
        print(result.summary())
        for key, (pinned, current) in result.drifted.items():
            print(f"  DRIFT {key}: pinned={pinned!r} current={current!r}")

    return 1 if result.has_drift() else 0
