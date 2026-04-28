"""Sanitizer: strip or replace characters in env config values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SanitizeResult:
    config: Dict[str, str]
    sanitized_keys: List[str] = field(default_factory=list)
    original: Dict[str, str] = field(default_factory=dict)

    def sanitize_count(self) -> int:  # noqa: D401
        return len(self.sanitized_keys)

    def has_sanitized(self) -> bool:
        return bool(self.sanitized_keys)

    def summary(self) -> str:
        total = len(self.config)
        changed = self.sanitize_count()
        if changed == 0:
            return f"All {total} values are clean — nothing sanitized."
        return (
            f"{changed} of {total} value(s) sanitized: "
            + ", ".join(self.sanitized_keys)
        )


_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _sanitize_value(
    value: str,
    *,
    strip_control: bool,
    replace_nulls: bool,
    replacement: str,
    allow_pattern: Optional[re.Pattern],  # type: ignore[type-arg]
) -> str:
    if replace_nulls:
        value = value.replace("\x00", replacement)
    if strip_control:
        value = _CONTROL_RE.sub(replacement, value)
    if allow_pattern is not None:
        value = allow_pattern.sub(replacement, value)
    return value


def sanitize_config(
    config: Dict[str, str],
    *,
    strip_control: bool = True,
    replace_nulls: bool = True,
    replacement: str = "",
    allow_only: Optional[str] = None,
) -> SanitizeResult:
    """Sanitize all values in *config*.

    Parameters
    ----------
    config:
        Mapping of env-var key → value.
    strip_control:
        Remove ASCII control characters (except ``\\t``, ``\\n``, ``\\r``).
    replace_nulls:
        Replace embedded NUL bytes.
    replacement:
        String used when replacing disallowed characters.
    allow_only:
        If provided, a regex character class (e.g. ``r"[^a-zA-Z0-9_.-]"``) —
        any character *not* matching is replaced.
    """
    allow_pattern: Optional[re.Pattern] = None  # type: ignore[type-arg]
    if allow_only:
        allow_pattern = re.compile(allow_only)

    result: Dict[str, str] = {}
    sanitized_keys: List[str] = []

    for key, value in config.items():
        clean = _sanitize_value(
            value,
            strip_control=strip_control,
            replace_nulls=replace_nulls,
            replacement=replacement,
            allow_pattern=allow_pattern,
        )
        result[key] = clean
        if clean != value:
            sanitized_keys.append(key)

    return SanitizeResult(
        config=result,
        sanitized_keys=sanitized_keys,
        original=dict(config),
    )
