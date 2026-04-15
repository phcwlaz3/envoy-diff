"""CLI sub-command handlers for snapshot operations."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from envoy_diff.loader import load_config
from envoy_diff.snapshotter import SnapshotError, list_snapshots, load_snapshot, save_snapshot


def add_snapshot_subparsers(subparsers) -> None:
    """Register 'snapshot' sub-commands onto the provided subparsers action."""
    snap_parser: ArgumentParser = subparsers.add_parser(
        "snapshot", help="Manage environment config snapshots"
    )
    snap_sub = snap_parser.add_subparsers(dest="snap_action", required=True)

    # snapshot save
    save_p = snap_sub.add_parser("save", help="Save a config snapshot")
    save_p.add_argument("file", help="Path to .env or .json config file")
    save_p.add_argument("--stage", required=True, help="Deployment stage name")
    save_p.add_argument("--dir", default=".envoy_snapshots", dest="output_dir")
    save_p.add_argument("--label", default=None, help="Optional snapshot label")

    # snapshot list
    list_p = snap_sub.add_parser("list", help="List saved snapshots for a stage")
    list_p.add_argument("--stage", required=True, help="Deployment stage name")
    list_p.add_argument("--dir", default=".envoy_snapshots", dest="output_dir")

    # snapshot load (print to stdout)
    load_p = snap_sub.add_parser("load", help="Print a snapshot config to stdout")
    load_p.add_argument("snapshot_file", help="Path to snapshot JSON file")


def run_snapshot_command(args: Namespace) -> int:
    """Dispatch snapshot sub-commands. Returns exit code."""
    if args.snap_action == "save":
        return _cmd_save(args)
    if args.snap_action == "list":
        return _cmd_list(args)
    if args.snap_action == "load":
        return _cmd_load(args)
    print(f"Unknown snapshot action: {args.snap_action}", file=sys.stderr)
    return 1


def _cmd_save(args: Namespace) -> int:
    try:
        config = load_config(args.file)
        path = save_snapshot(
            config,
            stage=args.stage,
            output_dir=args.output_dir,
            label=args.label,
        )
        print(f"Snapshot saved: {path}")
        return 0
    except (SnapshotError, Exception) as exc:  # noqa: BLE001
        print(f"Error saving snapshot: {exc}", file=sys.stderr)
        return 1


def _cmd_list(args: Namespace) -> int:
    snapshots = list_snapshots(args.stage, output_dir=args.output_dir)
    if not snapshots:
        print(f"No snapshots found for stage '{args.stage}'.")
        return 0
    for snap in snapshots:
        print(snap)
    return 0


def _cmd_load(args: Namespace) -> int:
    try:
        config = load_snapshot(args.snapshot_file)
        for key, value in sorted(config.items()):
            print(f"{key}={value}")
        return 0
    except SnapshotError as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        return 1
