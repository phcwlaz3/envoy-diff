"""Output formatters for DiffResult — supports text and JSON output."""

import json
from typing import Literal

from envoy_diff.differ import DiffResult

OutputFormat = Literal["text", "json"]


def format_diff(result: DiffResult, fmt: OutputFormat = "text", show_values: bool = True) -> str:
    """Format a DiffResult for display.

    Args:
        result: The DiffResult to format.
        fmt: Output format, either 'text' or 'json'.
        show_values: Whether to include actual values in the output.

    Returns:
        A formatted string representation of the diff.
    """
    if fmt == "json":
        return _format_json(result, show_values)
    return _format_text(result, show_values)


def _format_text(result: DiffResult, show_values: bool) -> str:
    lines = []

    for key, value in sorted(result.added.items()):
        val_str = f" = {value}" if show_values else ""
        lines.append(f"+ {key}{val_str}")

    for key, value in sorted(result.removed.items()):
        val_str = f" = {value}" if show_values else ""
        lines.append(f"- {key}{val_str}")

    for key, (old, new) in sorted(result.changed.items()):
        if show_values:
            lines.append(f"~ {key}  [{old}] -> [{new}]")
        else:
            lines.append(f"~ {key}")

    if not lines:
        return "No differences found."
    return "\n".join(lines)


def _format_json(result: DiffResult, show_values: bool) -> str:
    data: dict = {
        "added": list(result.added.keys()),
        "removed": list(result.removed.keys()),
        "changed": list(result.changed.keys()),
    }
    if show_values:
        data["added"] = result.added
        data["removed"] = result.removed
        data["changed"] = {
            k: {"from": old, "to": new} for k, (old, new) in result.changed.items()
        }
    return json.dumps(data, indent=2, sort_keys=True)
