"""Redactor module: mask sensitive values in env configs before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r"(?i)(password|passwd|secret|token|api_key|apikey|private_key|auth|credential)",
]

DEFAULT_MASK = "***REDACTED***"


@dataclass
class RedactionResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redacted_keys)

    def summary(self) -> str:
        if not self.redacted_keys:
            return "No sensitive keys detected."
        keys = ", ".join(sorted(self.redacted_keys))
        return f"{self.redaction_count} key(s) redacted: {keys}"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def redact_config(
    config: Dict[str, str],
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> RedactionResult:
    """Return a copy of config with sensitive values replaced by mask."""
    compiled = _compile_patterns(patterns or DEFAULT_SENSITIVE_PATTERNS)
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in config.items():
        if any(p.search(key) for p in compiled):
            redacted[key] = mask
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactionResult(
        original=dict(config),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )
