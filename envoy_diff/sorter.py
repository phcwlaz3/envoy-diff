"""Sort environment config keys by various strategies."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SortResult:
    config: Dict[str, str]
    strategy: str
    original_order: List[str] = field(default_factory=list)

    def key_count(self) -> int:
        return len(self.config)

    def summary(self) -> str:
        return f"Sorted {self.key_count()} keys using '{self.strategy}' strategy."


def sort_config(
    config: Dict[str, str],
    strategy: str = "alpha",
    reverse: bool = False,
) -> SortResult:
    """Sort config keys by the given strategy.

    Strategies:
      - alpha: alphabetical by key name
      - length: by key name length
      - value_length: by value length
    """
    original_order = list(config.keys())

    if strategy == "alpha":
        sorted_keys = sorted(config.keys(), reverse=reverse)
    elif strategy == "length":
        sorted_keys = sorted(config.keys(), key=len, reverse=reverse)
    elif strategy == "value_length":
        sorted_keys = sorted(config.keys(), key=lambda k: len(config[k]), reverse=reverse)
    else:
        raise ValueError(f"Unknown sort strategy: '{strategy}'. Choose alpha, length, or value_length.")

    sorted_config = {k: config[k] for k in sorted_keys}
    return SortResult(config=sorted_config, strategy=strategy, original_order=original_order)
