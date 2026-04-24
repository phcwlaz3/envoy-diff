"""Zip (pair) two env configs by key, producing aligned rows for comparison."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

_MISSING = "<missing>"


@dataclass
class ZipRow:
    key: str
    left: Optional[str]
    right: Optional[str]

    @property
    def is_aligned(self) -> bool:
        return self.left is not None and self.right is not None

    @property
    def is_equal(self) -> bool:
        return self.left == self.right


@dataclass
class ZipResult:
    rows: List[ZipRow] = field(default_factory=list)
    left_only: List[str] = field(default_factory=list)
    right_only: List[str] = field(default_factory=list)

    def aligned_count(self) -> int:
        return sum(1 for r in self.rows if r.is_aligned)

    def equal_count(self) -> int:
        return sum(1 for r in self.rows if r.is_equal)

    def diff_count(self) -> int:
        return sum(1 for r in self.rows if r.is_aligned and not r.is_equal)

    def summary(self) -> str:
        total = len(self.rows)
        aligned = self.aligned_count()
        diffs = self.diff_count()
        lo = len(self.left_only)
        ro = len(self.right_only)
        return (
            f"{total} keys zipped: {aligned} aligned, {diffs} differing, "
            f"{lo} left-only, {ro} right-only"
        )


def zip_configs(
    left: Dict[str, str],
    right: Dict[str, str],
    sort: bool = True,
) -> ZipResult:
    """Pair two configs by key into aligned ZipRows."""
    all_keys = set(left) | set(right)
    keys = sorted(all_keys) if sort else list(all_keys)

    rows: List[ZipRow] = []
    left_only: List[str] = []
    right_only: List[str] = []

    for key in keys:
        l_val = left.get(key)
        r_val = right.get(key)
        rows.append(ZipRow(key=key, left=l_val, right=r_val))
        if l_val is not None and r_val is None:
            left_only.append(key)
        elif r_val is not None and l_val is None:
            right_only.append(key)

    return ZipResult(rows=rows, left_only=left_only, right_only=right_only)
