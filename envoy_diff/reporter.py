"""Report generation for envoy-diff results."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

from envoy_diff.differ import DiffResult
from envoy_diff.validator import ValidationResult


@dataclass
class Report:
    """Aggregated report combining diff and validation results."""

    stage_a: str
    stage_b: str
    diff: Optional[DiffResult] = None
    validation_results: List[ValidationResult] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        """Return True if any diff or validation issues exist."""
        diff_has_changes = self.diff is not None and (
            bool(self.diff.added)
            or bool(self.diff.removed)
            or bool(self.diff.changed)
        )
        validation_failed = any(not vr for vr in self.validation_results)
        return diff_has_changes or validation_failed


def build_report(
    stage_a: str,
    stage_b: str,
    diff: Optional[DiffResult] = None,
    validation_results: Optional[List[ValidationResult]] = None,
) -> Report:
    """Construct a Report from diff and validation data."""
    return Report(
        stage_a=stage_a,
        stage_b=stage_b,
        diff=diff,
        validation_results=validation_results or [],
    )


def render_report(report: Report, fmt: str = "text") -> str:
    """Render a Report as text or JSON."""
    if fmt == "json":
        return _render_json(report)
    return _render_text(report)


def _render_text(report: Report) -> str:
    lines = [
        f"=== envoy-diff report: {report.stage_a} -> {report.stage_b} ===",
    ]

    if report.diff is not None:
        diff = report.diff
        lines.append(f"Added   : {len(diff.added)}")
        lines.append(f"Removed : {len(diff.removed)}")
        lines.append(f"Changed : {len(diff.changed)}")
        lines.append(f"Same    : {len(diff.unchanged)}")
    else:
        lines.append("Diff    : not performed")

    if report.validation_results:
        lines.append("Validation:")
        for vr in report.validation_results:
            status = "OK" if vr else "FAIL"
            lines.append(f"  [{status}] missing={vr.missing_keys} empty={vr.empty_keys}")
    else:
        lines.append("Validation: none")

    lines.append(f"Issues  : {'YES' if report.has_issues else 'NO'}")
    return "\n".join(lines)


def _render_json(report: Report) -> str:
    diff_data = None
    if report.diff is not None:
        d = report.diff
        diff_data = {
            "added": list(d.added),
            "removed": list(d.removed),
            "changed": list(d.changed),
            "unchanged": list(d.unchanged),
        }
    validation_data = [
        {"ok": bool(vr), "missing_keys": list(vr.missing_keys), "empty_keys": list(vr.empty_keys)}
        for vr in report.validation_results
    ]
    payload = {
        "stage_a": report.stage_a,
        "stage_b": report.stage_b,
        "diff": diff_data,
        "validation": validation_data,
        "has_issues": report.has_issues,
    }
    return json.dumps(payload, indent=2)
