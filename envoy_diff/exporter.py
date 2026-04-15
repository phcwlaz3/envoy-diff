"""Export diff reports to various output formats (file or stdout)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from envoy_diff.reporter import Report, render_report


class ExportError(Exception):
    """Raised when exporting a report fails."""


def export_report(
    report: Report,
    output_path: Optional[str] = None,
    fmt: str = "text",
) -> None:
    """Render *report* and write it to *output_path* or stdout.

    Args:
        report: The :class:`~envoy_diff.reporter.Report` to export.
        output_path: Filesystem path to write the output to.  When *None*
            the rendered content is written to *stdout*.
        fmt: Output format – either ``"text"`` (default) or ``"json"``.

    Raises:
        ExportError: If the output file cannot be written.
        ValueError: If *fmt* is not a supported format string.
    """
    supported = {"text", "json"}
    if fmt not in supported:
        raise ValueError(
            f"Unsupported export format {fmt!r}. Choose one of: {sorted(supported)}"
        )

    content = render_report(report, fmt=fmt)

    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Failed to write report to {output_path!r}: {exc}") from exc


def export_json_summary(report: Report, output_path: Optional[str] = None) -> None:
    """Write a compact JSON summary of *report* (issues count + pass/fail).

    This is a lightweight alternative to :func:`export_report` when only
    machine-readable metadata is needed (e.g. in CI pipelines).
    """
    summary = {
        "has_issues": report.has_issues,
        "diff_keys_added": len(report.diff.added),
        "diff_keys_removed": len(report.diff.removed),
        "diff_keys_changed": len(report.diff.changed),
        "validation_missing_keys": list(report.validation.missing_keys),
        "validation_empty_keys": list(report.validation.empty_keys),
        "validation_passed": bool(report.validation),
    }
    content = json.dumps(summary, indent=2)

    if output_path is None:
        sys.stdout.write(content + "\n")
        return

    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")
    except OSError as exc:
        raise ExportError(
            f"Failed to write JSON summary to {output_path!r}: {exc}"
        ) from exc
