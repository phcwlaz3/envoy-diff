"""Composer: build a config by composing named fragments together."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ComposeResult:
    config: Dict[str, str]
    fragments_used: List[str]
    skipped_fragments: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def fragment_count(self) -> int:
        return len(self.fragments_used)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        parts = [
            f"{self.fragment_count} fragment(s) composed",
            f"{len(self.config)} key(s) total",
        ]
        if self.skipped_fragments:
            parts.append(f"{len(self.skipped_fragments)} skipped")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflict(s)")
        return ", ".join(parts)


def compose_configs(
    fragments: Dict[str, Dict[str, str]],
    order: Optional[List[str]] = None,
    on_conflict: str = "last_wins",
) -> ComposeResult:
    """Compose multiple named config fragments into one config.

    Args:
        fragments: mapping of fragment name -> config dict.
        order: optional list of fragment names defining merge order.
                Fragments not in *order* are appended alphabetically.
        on_conflict: ``'last_wins'`` (default) or ``'first_wins'``.
    """
    if order is None:
        order = sorted(fragments.keys())
    else:
        # append any fragments not explicitly ordered
        order = list(order) + sorted(k for k in fragments if k not in order)

    composed: Dict[str, str] = {}
    used: List[str] = []
    skipped: List[str] = []
    conflicts: List[str] = []

    for name in order:
        if name not in fragments:
            skipped.append(name)
            continue
        used.append(name)
        for key, value in fragments[name].items():
            if key in composed:
                if composed[key] != value:
                    conflicts.append(key)
                if on_conflict == "first_wins":
                    continue
            composed[key] = value

    # deduplicate conflicts list while preserving order
    seen: set = set()
    deduped_conflicts = []
    for c in conflicts:
        if c not in seen:
            seen.add(c)
            deduped_conflicts.append(c)

    return ComposeResult(
        config=composed,
        fragments_used=used,
        skipped_fragments=skipped,
        conflicts=deduped_conflicts,
    )
