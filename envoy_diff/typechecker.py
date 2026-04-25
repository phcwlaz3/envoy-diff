"""Type-checking module for env config values.

Validates that config values conform to expected types
(int, float, bool, url, email, etc.).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_TYPE_PATTERNS: Dict[str, re.Pattern] = {
    "int": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.\d+$"),
    "bool": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "url": re.compile(r"^https?://[^\s]+$", re.IGNORECASE),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "port": re.compile(r"^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$"),
}


@dataclass
class TypeViolation:
    key: str
    value: str
    expected_type: str

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "expected_type": self.expected_type}


@dataclass
class TypeCheckResult:
    checked: Dict[str, str]
    violations: List[TypeViolation] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    def summary(self) -> str:
        total = len(self.checked)
        v = self.violation_count
        if v == 0:
            return f"All {total} checked value(s) pass type constraints."
        return f"{v} of {total} value(s) failed type constraints."


def _check_value(value: str, expected_type: str) -> bool:
    """Return True if *value* matches *expected_type*."""
    pattern = _TYPE_PATTERNS.get(expected_type)
    if pattern is None:
        return True  # unknown type — skip
    return bool(pattern.match(value))


def typecheck_config(
    config: Dict[str, str],
    rules: Dict[str, str],
) -> TypeCheckResult:
    """Check *config* values against *rules* mapping key -> expected_type.

    Only keys present in both *config* and *rules* are checked.
    """
    checked: Dict[str, str] = {}
    violations: List[TypeViolation] = []

    for key, expected_type in rules.items():
        if key not in config:
            continue
        value = config[key]
        checked[key] = value
        if not _check_value(value, expected_type):
            violations.append(TypeViolation(key=key, value=value, expected_type=expected_type))

    return TypeCheckResult(checked=checked, violations=violations)
