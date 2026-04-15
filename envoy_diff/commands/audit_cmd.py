"""CLI sub-commands for the audit feature."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_diff.auditor import AuditError, AuditLog, create_entry, load_audit_log, save_audit_log
from envoy_diff.differ import diff_configs
from envoy_diff.loader import load_config
from envoy_diff.validator import validate_config


def add_audit_subparsers(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    audit_parser = sub.add_parser("audit", help="Audit diff runs")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd", required=True)

    # audit record
    record_p = audit_sub.add_parser("record", help="Record a diff run to the audit log")
    record_p.add_argument("file_a", help="First env file (stage A)")
    record_p.add_argument("file_b", help="Second env file (stage B)")
    record_p.add_argument("--label", default=None, help="Optional run label")
    record_p.add_argument(
        "--audit-log", default=".envoy_audit.json", dest="audit_log", metavar="PATH"
    )
    record_p.add_argument("--required-keys", nargs="*", default=[], dest="required_keys")

    # audit show
    show_p = audit_sub.add_parser("show", help="Print audit log entries")
    show_p.add_argument(
        "--audit-log", default=".envoy_audit.json", dest="audit_log", metavar="PATH"
    )
    show_p.add_argument("--format", choices=["text", "json"], default="text")


def run_audit_command(args: argparse.Namespace) -> int:
    cmd = args.audit_cmd
    if cmd == "record":
        return _cmd_record(args)
    if cmd == "show":
        return _cmd_show(args)
    print(f"Unknown audit command: {cmd}", file=sys.stderr)
    return 1


def _cmd_record(args: argparse.Namespace) -> int:
    try:
        cfg_a = load_config(args.file_a)
        cfg_b = load_config(args.file_b)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    result = diff_configs(cfg_a, cfg_b)
    val_result = validate_config(cfg_b, required_keys=args.required_keys)

    entry = create_entry(
        stage_a=args.file_a,
        stage_b=args.file_b,
        has_diff=result.has_diff,
        validation_passed=bool(val_result),
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        label=args.label,
    )
    log = AuditLog(entries=[entry])
    try:
        save_audit_log(log, Path(args.audit_log))
    except AuditError as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 1

    print(f"Audit entry recorded to {args.audit_log}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    try:
        log = load_audit_log(Path(args.audit_log))
    except AuditError as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(log.to_dict(), indent=2))
        return 0

    if not log.entries:
        print("No audit entries found.")
        return 0

    for idx, entry in enumerate(log.entries, 1):
        status = "PASS" if entry.validation_passed else "FAIL"
        diff_flag = "YES" if entry.has_diff else "NO"
        label_str = f" [{entry.label}]" if entry.label else ""
        print(
            f"{idx:>3}. {entry.timestamp}{label_str}  "
            f"{entry.stage_a} -> {entry.stage_b}  "
            f"diff={diff_flag}  +{entry.added}/-{entry.removed}/~{entry.changed}  "
            f"validation={status}"
        )
    return 0
