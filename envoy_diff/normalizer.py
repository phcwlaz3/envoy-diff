"""Normalizer: strip, case-fold, and canonicalize env config values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "No normalization changes applied."
        lines = [f"Normalized {self.change_count} value(s):"]
        for c in self.changes:
            lines.append(f"  - {c}")
        return "\n".join(lines)


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _normalize_boolean(value: str) -> str:
    """Canonicalize boolean-like strings to lowercase 'true'/'false'."""
    if value.lower() in ("true", "yes", "1", "on"):
        return "true"
    if value.lower() in ("false", "no", "0", "off"):
        return "false"
    return value


def normalize_config(
    config: Dict[str, str],
    strip_quotes: bool = True,
    normalize_booleans: bool = True,
    strip_whitespace: bool = True,
) -> NormalizeResult:
    """Return a NormalizeResult with cleaned-up config values."""
    normalized: Dict[str, str] = {}
    changes: List[str] = []

    for key, raw_value in config.items():
        value = raw_value

        if strip_whitespace:
            value = value.strip()

        if strip_quotes:
            value = _strip_quotes(value)

        if normalize_booleans:
            value = _normalize_boolean(value)

        if value != raw_value:
            changes.append(f"{key}: {raw_value!r} -> {value!r}")

        normalized[key] = value

    return NormalizeResult(original=config, normalized=normalized, changes=changes)
