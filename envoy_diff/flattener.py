"""Flatten nested JSON/dict configs into dot-notation env-style keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FlattenResult:
    config: dict[str, str]
    original_key_count: int
    flattened_key_count: int
    _summary: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._summary = (
            f"Flattened {self.original_key_count} keys into "
            f"{self.flattened_key_count} dot-notation keys."
        )

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def key_count(self) -> int:
        return self.flattened_key_count


def _flatten(obj: Any, prefix: str = "", sep: str = ".") -> dict[str, str]:
    items: dict[str, str] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}{sep}{k}" if prefix else k
            items.update(_flatten(v, new_key, sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}{sep}{i}" if prefix else str(i)
            items.update(_flatten(v, new_key, sep))
    else:
        items[prefix] = str(obj) if obj is not None else ""
    return items


def flatten_config(
    config: dict[str, Any],
    sep: str = ".",
    uppercase_keys: bool = False,
) -> FlattenResult:
    """Flatten a nested config dict into a flat string mapping."""
    original_count = len(config)
    flat = _flatten(config, sep=sep)
    if uppercase_keys:
        flat = {k.upper().replace(sep, "_"): v for k, v in flat.items()}
    return FlattenResult(
        config=flat,
        original_key_count=original_count,
        flattened_key_count=len(flat),
    )
