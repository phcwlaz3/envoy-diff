from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ExtractResult:
    extracted: Dict[str, str]
    skipped: List[str] = field(default_factory=list)
    pattern: Optional[str] = None

    def extract_count(self) -> int:
        return len(self.extracted)

    def has_skipped(self) -> bool:
        return len(self.skipped) > 0

    def summary(self) -> str:
        parts = [f"extracted={self.extract_count()}"]
        if self.skipped:
            parts.append(f"skipped={len(self.skipped)}")
        if self.pattern:
            parts.append(f"pattern={self.pattern!r}")
        return ", ".join(parts)


def extract_config(
    config: Dict[str, str],
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
) -> ExtractResult:
    """Extract a subset of keys from a config by explicit list, regex pattern, or prefix."""
    extracted: Dict[str, str] = {}
    skipped: List[str] = []
    compiled = re.compile(pattern) if pattern else None

    for key, value in config.items():
        matched = False
        if keys and key in keys:
            matched = True
        elif compiled and compiled.search(key):
            matched = True
        elif prefix and key.startswith(prefix):
            matched = True

        if matched:
            extracted[key] = value
        else:
            skipped.append(key)

    return ExtractResult(extracted=extracted, skipped=skipped, pattern=pattern)
