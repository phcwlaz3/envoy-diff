from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ExpandResult:
    config: Dict[str, str]
    expanded: Dict[str, List[str]]
    expand_count: int = 0

    def has_expanded(self) -> bool:
        return self.expand_count > 0

    def summary(self) -> str:
        if not self.has_expanded():
            return "No keys expanded."
        keys = ", ".join(sorted(self.expanded.keys()))
        return f"Expanded {self.expand_count} key(s): {keys}"


def expand_config(
    config: Dict[str, str],
    delimiter: str = ",",
    suffix_template: str = "_{i}",
) -> ExpandResult:
    """Expand multi-value keys (comma-separated by default) into indexed sub-keys."""
    result: Dict[str, str] = {}
    expanded: Dict[str, List[str]] = {}

    for key, value in config.items():
        parts = [p.strip() for p in value.split(delimiter)]
        if len(parts) <= 1:
            result[key] = value
            continue

        sub_keys: List[str] = []
        for i, part in enumerate(parts, start=1):
            suffix = suffix_template.replace("{i}", str(i))
            new_key = f"{key}{suffix}"
            result[new_key] = part
            sub_keys.append(new_key)

        expanded[key] = sub_keys

    return ExpandResult(
        config=result,
        expanded=expanded,
        expand_count=len(expanded),
    )
