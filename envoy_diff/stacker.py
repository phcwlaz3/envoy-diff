"""Stack multiple env configs into a layered view, showing effective value per key."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class StackEntry:
    key: str
    effective_value: str
    source_index: int  # index of the layer that provided the effective value
    all_values: List[Tuple[int, str]] = field(default_factory=list)  # (layer_idx, value)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "effective_value": self.effective_value,
            "source_index": self.source_index,
            "all_values": [{"layer": idx, "value": val} for idx, val in self.all_values],
        }


@dataclass
class StackResult:
    entries: Dict[str, StackEntry] = field(default_factory=dict)
    layer_count: int = 0
    override_count: int = 0  # keys that differ across at least two layers

    def summary(self) -> str:
        return (
            f"{len(self.entries)} keys across {self.layer_count} layers, "
            f"{self.override_count} overridden"
        )

    def to_dict(self) -> dict:
        return {
            "layer_count": self.layer_count,
            "override_count": self.override_count,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
        }


def stack_configs(
    layers: List[Dict[str, str]],
    strategy: str = "last-wins",
) -> StackResult:
    """Merge a list of env config dicts into a stacked view.

    Args:
        layers: Ordered list of config dicts; later layers take precedence by default.
        strategy: 'last-wins' (default) or 'first-wins'.
    """
    if not layers:
        return StackResult(layer_count=0)

    all_keys: List[str] = []
    for layer in layers:
        for k in layer:
            if k not in all_keys:
                all_keys.append(k)

    entries: Dict[str, StackEntry] = {}
    override_count = 0

    for key in all_keys:
        seen: List[Tuple[int, str]] = [
            (idx, layer[key]) for idx, layer in enumerate(layers) if key in layer
        ]
        if not seen:
            continue

        if strategy == "first-wins":
            source_index, effective_value = seen[0]
        else:
            source_index, effective_value = seen[-1]

        unique_values = {v for _, v in seen}
        if len(unique_values) > 1:
            override_count += 1

        entries[key] = StackEntry(
            key=key,
            effective_value=effective_value,
            source_index=source_index,
            all_values=seen,
        )

    return StackResult(
        entries=entries,
        layer_count=len(layers),
        override_count=override_count,
    )
