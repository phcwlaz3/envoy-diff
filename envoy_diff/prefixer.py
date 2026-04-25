"""Prefixer: add or strip a prefix from all config keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PrefixResult:
    original: Dict[str, str]
    result: Dict[str, str]
    changed_keys: list = field(default_factory=list)
    mode: str = "add"  # "add" | "strip"
    prefix: str = ""

    def change_count(self) -> int:
        return len(self.changed_keys)

    def has_changes(self) -> bool:
        return bool(self.changed_keys)

    def summary(self) -> str:
        if not self.has_changes():
            return f"No keys {self.mode}ed prefix '{self.prefix}'."
        action = "prefixed" if self.mode == "add" else "stripped"
        return (
            f"{self.change_count()} key(s) {action} with '{self.prefix}'."
        )


def add_prefix(
    config: Dict[str, str],
    prefix: str,
    *,
    skip_already_prefixed: bool = True,
) -> PrefixResult:
    """Return a new config where every key is prefixed with *prefix*."""
    result: Dict[str, str] = {}
    changed: list = []

    for key, value in config.items():
        if skip_already_prefixed and key.startswith(prefix):
            result[key] = value
        else:
            new_key = f"{prefix}{key}"
            result[new_key] = value
            changed.append(key)

    return PrefixResult(
        original=dict(config),
        result=result,
        changed_keys=changed,
        mode="add",
        prefix=prefix,
    )


def strip_prefix(
    config: Dict[str, str],
    prefix: str,
    *,
    keep_unmatched: bool = True,
) -> PrefixResult:
    """Return a new config with *prefix* removed from matching keys."""
    result: Dict[str, str] = {}
    changed: list = []

    for key, value in config.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            result[new_key] = value
            changed.append(key)
        elif keep_unmatched:
            result[key] = value

    return PrefixResult(
        original=dict(config),
        result=result,
        changed_keys=changed,
        mode="strip",
        prefix=prefix,
    )
