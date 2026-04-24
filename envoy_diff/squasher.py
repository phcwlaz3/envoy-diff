"""Squasher: merge consecutive duplicate values into a single representative entry."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SquashResult:
    config: Dict[str, str]
    squashed: Dict[str, List[str]]  # representative key -> list of squashed keys
    original_count: int

    def squash_count(self) -> int:
        """Total number of keys that were removed by squashing."""
        return sum(len(v) - 1 for v in self.squashed.values() if v)

    def has_squashed(self) -> bool:
        return bool(self.squashed)

    def summary(self) -> str:
        if not self.has_squashed():
            return f"No duplicate values found across {self.original_count} keys."
        groups = len(self.squashed)
        removed = self.squash_count()
        return (
            f"Squashed {removed} redundant key(s) across {groups} group(s) "
            f"({self.original_count} -> {len(self.config)} keys)."
        )


def squash_config(
    config: Dict[str, str],
    keep: str = "first",
) -> SquashResult:
    """Squash keys that share identical values.

    Args:
        config: Input key/value mapping.
        keep: Which key to treat as the representative — ``'first'`` (default)
              keeps the key that appears earliest; ``'last'`` keeps the latest;
              ``'shortest'`` keeps the lexicographically shortest key name.

    Returns:
        A :class:`SquashResult` containing the reduced config and metadata.
    """
    if keep not in {"first", "last", "shortest"}:
        raise ValueError(f"Invalid keep strategy '{keep}'. Choose first, last, or shortest.")

    # Group keys by value
    value_to_keys: Dict[str, List[str]] = {}
    for key, value in config.items():
        value_to_keys.setdefault(value, []).append(key)

    squashed: Dict[str, List[str]] = {}
    result: Dict[str, str] = {}

    # Preserve original insertion order for output
    seen_values: Dict[str, str] = {}  # value -> chosen representative key

    for key, value in config.items():
        group = value_to_keys[value]
        if len(group) == 1:
            result[key] = value
            continue

        if value in seen_values:
            # Already have a representative — skip this key
            rep = seen_values[value]
            squashed[rep].append(key)
            continue

        # Choose representative from the group
        if keep == "first":
            rep = group[0]
        elif keep == "last":
            rep = group[-1]
        else:  # shortest
            rep = min(group, key=lambda k: (len(k), k))

        seen_values[value] = rep
        squashed[rep] = [k for k in group if k != rep]

        if key == rep:
            result[key] = value
        # else: rep will be added when we reach it in iteration order

    # Ensure representatives that appear later in iteration are still added
    for key, value in config.items():
        if key not in result and value in seen_values and seen_values[value] == key:
            result[key] = value

    return SquashResult(
        config=result,
        squashed=squashed,
        original_count=len(config),
    )
