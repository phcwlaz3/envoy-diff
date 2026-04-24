"""Key-value config differ with line-level context tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeltaEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    left_value: Optional[str] = None
    right_value: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "status": self.status,
            "left_value": self.left_value,
            "right_value": self.right_value,
        }


@dataclass
class DeltaResult:
    entries: List[DeltaEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DeltaEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[DeltaEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[DeltaEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def unchanged(self) -> List[DeltaEntry]:
        return [e for e in self.entries if e.status == "unchanged"]

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        return (
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.changed)} changed, "
            f"={len(self.unchanged)} unchanged"
        )

    def to_dict(self) -> dict:
        return {
            "added": [e.to_dict() for e in self.added],
            "removed": [e.to_dict() for e in self.removed],
            "changed": [e.to_dict() for e in self.changed],
            "unchanged": [e.to_dict() for e in self.unchanged],
            "summary": self.summary(),
        }


def delta_configs(
    left: Dict[str, str],
    right: Dict[str, str],
    *,
    include_unchanged: bool = True,
) -> DeltaResult:
    """Compute a per-key delta between two env configs."""
    entries: List[DeltaEntry] = []
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            entries.append(DeltaEntry(key=key, status="removed", left_value=left[key]))
        elif in_right and not in_left:
            entries.append(DeltaEntry(key=key, status="added", right_value=right[key]))
        elif left[key] != right[key]:
            entries.append(
                DeltaEntry(
                    key=key,
                    status="changed",
                    left_value=left[key],
                    right_value=right[key],
                )
            )
        elif include_unchanged:
            entries.append(
                DeltaEntry(
                    key=key,
                    status="unchanged",
                    left_value=left[key],
                    right_value=right[key],
                )
            )

    return DeltaResult(entries=entries)
