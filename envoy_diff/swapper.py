"""Swap keys and values or swap values between two keys in a config."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SwapResult:
    config: Dict[str, str]
    swapped: List[Tuple[str, str]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def swap_count(self) -> int:
        return len(self.swapped)

    def has_swaps(self) -> bool:
        return bool(self.swapped)

    def summary(self) -> str:
        if not self.swapped:
            return "No swaps performed."
        pairs = ", ".join(f"{a}<->{b}" for a, b in self.swapped)
        parts = [f"Swapped {self.swap_count()} pair(s): {pairs}"]
        if self.skipped:
            parts.append(f"Skipped {len(self.skipped)} missing key(s): {', '.join(self.skipped)}")
        return " | ".join(parts)


def swap_config(
    config: Dict[str, str],
    pairs: Optional[List[Tuple[str, str]]] = None,
) -> SwapResult:
    """Swap values between pairs of keys.

    If *pairs* is None or empty, return the config unchanged.
    Each tuple ``(a, b)`` swaps the values of keys *a* and *b*.
    If either key is missing the pair is recorded in *skipped*.
    """
    if not pairs:
        return SwapResult(config=dict(config))

    result: Dict[str, str] = dict(config)
    swapped: List[Tuple[str, str]] = []
    skipped: List[str] = []

    for key_a, key_b in pairs:
        missing = [k for k in (key_a, key_b) if k not in result]
        if missing:
            skipped.extend(missing)
            continue
        result[key_a], result[key_b] = result[key_b], result[key_a]
        swapped.append((key_a, key_b))

    return SwapResult(config=result, swapped=swapped, skipped=skipped)
