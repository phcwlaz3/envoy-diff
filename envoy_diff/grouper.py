"""Group environment variables by prefix or custom rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def group_count(self) -> int:
        return len(self.groups)

    def summary(self) -> str:
        parts = [f"{name}({len(keys)}k)" for name, keys in self.groups.items()]
        ug = len(self.ungrouped)
        base = f"Groups: {', '.join(parts)}" if parts else "No groups"
        return base + (f"; ungrouped: {ug}" if ug else "")


def _detect_prefix(key: str, sep: str = "_") -> Optional[str]:
    idx = key.find(sep)
    if idx > 0:
        return key[:idx]
    return None


def group_config(
    config: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    sep: str = "_",
    auto_detect: bool = True,
) -> GroupResult:
    """Group keys by explicit prefixes or auto-detected common prefixes."""
    effective: List[str] = list(prefixes or [])

    if auto_detect:
        detected: Dict[str, int] = {}
        for key in config:
            p = _detect_prefix(key, sep)
            if p:
                detected[p] = detected.get(p, 0) + 1
        for p, count in detected.items():
            if count >= 2 and p not in effective:
                effective.append(p)

    groups: Dict[str, Dict[str, str]] = {p: {} for p in effective}
    ungrouped: Dict[str, str] = {}

    for key, value in config.items():
        matched = False
        for p in effective:
            if key.startswith(p + sep) or key == p:
                groups[p][key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    # drop empty groups
    groups = {k: v for k, v in groups.items() if v}
    return GroupResult(groups=groups, ungrouped=ungrouped)
