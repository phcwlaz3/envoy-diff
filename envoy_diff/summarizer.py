from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SummaryResult:
    total_keys: int
    unique_values: int
    empty_keys: List[str]
    duplicate_values: Dict[str, List[str]]
    longest_key: str
    longest_value_key: str

    def empty_count(self) -> int:
        return len(self.empty_keys)

    def duplicate_group_count(self) -> int:
        return len(self.duplicate_values)

    def summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Unique values   : {self.unique_values}",
            f"Empty keys      : {self.empty_count()}",
            f"Duplicate groups: {self.duplicate_group_count()}",
            f"Longest key     : {self.longest_key}",
            f"Longest value at: {self.longest_value_key}",
        ]
        return "\n".join(lines)


def summarize_config(config: Dict[str, str]) -> SummaryResult:
    if not config:
        return SummaryResult(
            total_keys=0,
            unique_values=0,
            empty_keys=[],
            duplicate_values={},
            longest_key="",
            longest_value_key="",
        )

    total_keys = len(config)
    unique_values = len(set(config.values()))

    empty_keys = [k for k, v in config.items() if v == ""]

    value_map: Dict[str, List[str]] = {}
    for k, v in config.items():
        value_map.setdefault(v, []).append(k)
    duplicate_values = {v: keys for v, keys in value_map.items() if len(keys) > 1}

    longest_key = max(config.keys(), key=len)
    longest_value_key = max(config.keys(), key=lambda k: len(config[k]))

    return SummaryResult(
        total_keys=total_keys,
        unique_values=unique_values,
        empty_keys=empty_keys,
        duplicate_values=duplicate_values,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )
