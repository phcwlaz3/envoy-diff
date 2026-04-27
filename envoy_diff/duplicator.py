"""Duplicator: copy keys under new names within a config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    config: Dict[str, str]
    duplicated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def duplicate_count(self) -> int:
        return len(self.duplicated)

    def has_duplicates(self) -> bool:
        return bool(self.duplicated)

    def summary(self) -> str:
        if not self.duplicated:
            return "No keys duplicated."
        parts = [f"Duplicated {self.duplicate_count()} key(s): {', '.join(self.duplicated)}"]
        if self.skipped:
            parts.append(f"Skipped {len(self.skipped)} key(s) (target already exists): {', '.join(self.skipped)}")
        return ". ".join(parts) + "."


def duplicate_config(
    config: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> DuplicateResult:
    """Copy values from source keys to target keys.

    Args:
        config:    The original key/value mapping.
        mapping:   Dict of {source_key: target_key} pairs.
        overwrite: If True, overwrite an existing target key.

    Returns:
        DuplicateResult with updated config and bookkeeping lists.
    """
    result = dict(config)
    duplicated: List[str] = []
    skipped: List[str] = []

    for source, target in mapping.items():
        if source not in config:
            skipped.append(source)
            continue
        if target in result and not overwrite:
            skipped.append(source)
            continue
        result[target] = config[source]
        duplicated.append(source)

    return DuplicateResult(config=result, duplicated=duplicated, skipped=skipped)
