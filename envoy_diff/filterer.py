"""Filter environment config keys by pattern, prefix, or category."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    filtered: Dict[str, str]
    excluded: List[str]
    original_count: int

    def kept_count(self) -> int:
        return len(self.filtered)

    def excluded_count(self) -> int:
        return len(self.excluded)

    def summary(self) -> str:
        return (
            f"Kept {self.kept_count()}/{self.original_count} keys "
            f"({self.excluded_count()} excluded)"
        )


def filter_config(
    config: Dict[str, str],
    *,
    include_prefix: Optional[str] = None,
    exclude_prefix: Optional[str] = None,
    include_pattern: Optional[str] = None,
    exclude_pattern: Optional[str] = None,
    keys: Optional[List[str]] = None,
) -> FilterResult:
    """Return a filtered copy of config based on the given criteria."""
    original_count = len(config)
    filtered: Dict[str, str] = {}
    excluded: List[str] = []

    try:
        inc_re = re.compile(include_pattern) if include_pattern else None
        exc_re = re.compile(exclude_pattern) if exclude_pattern else None
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}") from e

    for key, value in config.items():
        keep = True

        if keys is not None and key not in keys:
            keep = False
        if include_prefix and not key.startswith(include_prefix):
            keep = False
        if exclude_prefix and key.startswith(exclude_prefix):
            keep = False
        if inc_re and not inc_re.search(key):
            keep = False
        if exc_re and exc_re.search(key):
            keep = False

        if keep:
            filtered[key] = value
        else:
            excluded.append(key)

    return FilterResult(
        filtered=filtered,
        excluded=excluded,
        original_count=original_count,
    )
