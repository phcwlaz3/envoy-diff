"""Map environment variable keys from one name to a target schema using a mapping definition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class MapResult:
    mapped: Dict[str, str]
    mapping_applied: List[str] = field(default_factory=list)
    unmapped: List[str] = field(default_factory=list)

    def map_count(self) -> int:
        return len(self.mapping_applied)

    def has_unmapped(self) -> bool:
        return len(self.unmapped) > 0

    def summary(self) -> str:
        parts = [f"{self.map_count()} key(s) mapped"]
        if self.unmapped:
            parts.append(f"{len(self.unmapped)} unmapped")
        return ", ".join(parts)


def _compile_pattern(pattern: str) -> re.Pattern:
    return re.compile(pattern)


def map_config(
    config: Dict[str, str],
    explicit: Optional[Dict[str, str]] = None,
    patterns: Optional[Dict[str, str]] = None,
    drop_unmapped: bool = False,
) -> MapResult:
    """Map keys in *config* to new names.

    Args:
        config: Source key/value pairs.
        explicit: Direct old->new key mappings.
        patterns: Regex pattern->replacement mappings (applied to key names).
        drop_unmapped: If True, keys that have no mapping are excluded from output.

    Returns:
        MapResult with the remapped config and metadata.
    """
    explicit = explicit or {}
    patterns = patterns or {}

    mapped: Dict[str, str] = {}
    mapping_applied: List[str] = []
    unmapped: List[str] = []

    compiled = [(re.compile(pat), repl) for pat, repl in patterns.items()]

    for key, value in config.items():
        new_key: Optional[str] = None

        if key in explicit:
            new_key = explicit[key]
        else:
            for pattern, replacement in compiled:
                if pattern.search(key):
                    new_key = pattern.sub(replacement, key)
                    break

        if new_key is not None:
            mapped[new_key] = value
            mapping_applied.append(key)
        else:
            unmapped.append(key)
            if not drop_unmapped:
                mapped[key] = value

    return MapResult(
        mapped=mapped,
        mapping_applied=mapping_applied,
        unmapped=unmapped,
    )
