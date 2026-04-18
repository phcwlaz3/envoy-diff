"""Count and report key/value statistics across a config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CountResult:
    total: int
    by_prefix: Dict[str, int]
    by_value_type: Dict[str, int]  # str, int, bool, empty
    longest_keys: List[str]
    longest_values: List[str]

    def summary(self) -> str:
        parts = [f"total={self.total}"]
        if self.by_prefix:
            top = sorted(self.by_prefix.items(), key=lambda x: -x[1])[:3]
            parts.append("prefixes=[" + ", ".join(f"{p}:{n}" for p, n in top) + "]")
        parts.append(
            "types=[" + ", ".join(f"{t}:{n}" for t, n in self.by_value_type.items()) + "]"
        )
        return " ".join(parts)


def _detect_prefix(key: str) -> str | None:
    if "_" in key:
        return key.split("_")[0]
    return None


def _classify_value(value: str) -> str:
    if value == "":
        return "empty"
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def count_config(config: Dict[str, str], top_n: int = 5) -> CountResult:
    """Compute key/value statistics for *config*."""
    by_prefix: Dict[str, int] = {}
    by_value_type: Dict[str, int] = {}

    for key, value in config.items():
        prefix = _detect_prefix(key)
        if prefix:
            by_prefix[prefix] = by_prefix.get(prefix, 0) + 1

        vtype = _classify_value(value)
        by_value_type[vtype] = by_value_type.get(vtype, 0) + 1

    longest_keys = sorted(config.keys(), key=len, reverse=True)[:top_n]
    longest_values = sorted(config.keys(), key=lambda k: len(config[k]), reverse=True)[:top_n]

    return CountResult(
        total=len(config),
        by_prefix=by_prefix,
        by_value_type=by_value_type,
        longest_keys=longest_keys,
        longest_values=longest_values,
    )
