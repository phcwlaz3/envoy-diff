"""Strip keys or values from a config based on criteria."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class StripResult:
    config: Dict[str, str]
    stripped_keys: List[str] = field(default_factory=list)

    def strip_count(self) -> int:
        return len(self.stripped_keys)

    def has_stripped(self) -> bool:
        return bool(self.stripped_keys)

    def summary(self) -> str:
        if not self.has_stripped():
            return "No keys stripped."
        return f"Stripped {self.strip_count()} key(s): {', '.join(self.stripped_keys)}"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def strip_config(
    config: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    strip_empty: bool = False,
    strip_whitespace_values: bool = False,
) -> StripResult:
    """Return a new config with matching keys removed."""
    explicit = set(keys or [])
    compiled = _compile_patterns(patterns or [])
    result: Dict[str, str] = {}
    stripped: List[str] = []

    for k, v in config.items():
        if k in explicit:
            stripped.append(k)
            continue
        if any(p.search(k) for p in compiled):
            stripped.append(k)
            continue
        if strip_empty and v == "":
            stripped.append(k)
            continue
        if strip_whitespace_values and v.strip() == "":
            stripped.append(k)
            continue
        result[k] = v

    return StripResult(config=result, stripped_keys=stripped)
