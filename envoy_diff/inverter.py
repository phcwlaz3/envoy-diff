"""Invert a config: swap keys and values, reporting collisions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class InvertResult:
    inverted: Dict[str, str]
    collisions: List[str] = field(default_factory=list)
    original_count: int = 0

    def collision_count(self) -> int:  # noqa: D401
        return len(self.collisions)

    def has_collisions(self) -> bool:
        return bool(self.collisions)

    def summary(self) -> str:
        parts = [
            f"{self.original_count} key(s) processed",
            f"{len(self.inverted)} unique value(s) kept",
        ]
        if self.has_collisions():
            parts.append(
                f"{self.collision_count()} collision(s): {', '.join(self.collisions)}"
            )
        return "; ".join(parts)


def invert_config(
    config: Dict[str, str],
    *,
    on_collision: str = "last",
) -> InvertResult:
    """Return a new dict with keys and values swapped.

    Parameters
    ----------
    config:
        Source key-value mapping.
    on_collision:
        Strategy when multiple keys share the same value.
        ``"first"`` keeps the first key seen; ``"last"`` (default) keeps the
        last key seen.

    Returns
    -------
    InvertResult
    """
    if on_collision not in {"first", "last"}:
        raise ValueError(f"on_collision must be 'first' or 'last', got {on_collision!r}")

    inverted: Dict[str, str] = {}
    seen: Dict[str, str] = {}   # value -> first key that produced it
    collisions: List[str] = []

    for key, value in config.items():
        str_value = str(value)
        if str_value in seen:
            # Collision detected
            if str_value not in collisions:
                collisions.append(str_value)
            if on_collision == "last":
                inverted[str_value] = key
            # on_collision == "first": leave existing entry untouched
        else:
            seen[str_value] = key
            inverted[str_value] = key

    return InvertResult(
        inverted=inverted,
        collisions=collisions,
        original_count=len(config),
    )
