"""Split a config into multiple files by prefix or category."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    buckets: Dict[str, Dict[str, str]]
    unmatched: Dict[str, str]
    _prefixes: List[str]

    def bucket_count(self) -> int:
        return len(self.buckets)

    def has_unmatched(self) -> bool:
        return bool(self.unmatched)

    def summary(self) -> str:
        parts = [f"{len(v)} key(s) in '{k}'" for k, v in self.buckets.items()]
        if self.unmatched:
            parts.append(f"{len(self.unmatched)} unmatched")
        return "; ".join(parts) if parts else "no keys"


def split_config(
    config: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    auto: bool = False,
) -> SplitResult:
    """Split config keys into buckets by prefix.

    If *auto* is True and no prefixes are supplied, detect prefixes
    automatically (same heuristic as grouper: prefix = first segment
    before '_' that appears on 2+ keys).
    """
    if not prefixes and auto:
        prefixes = _auto_detect_prefixes(config)

    prefixes = prefixes or []
    buckets: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    unmatched: Dict[str, str] = {}

    for key, value in config.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix + "_") or key == prefix:
                buckets[prefix][key] = value
                matched = True
                break
        if not matched:
            unmatched[key] = value

    return SplitResult(buckets=buckets, unmatched=unmatched, _prefixes=prefixes)


def _auto_detect_prefixes(config: Dict[str, str]) -> List[str]:
    from collections import Counter
    counts: Counter = Counter()
    for key in config:
        if "_" in key:
            counts[key.split("_")[0]] += 1
    return [p for p, c in counts.items() if c >= 2]
