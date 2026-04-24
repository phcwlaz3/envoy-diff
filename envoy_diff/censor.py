"""Censor module: replace values of matched keys with a fixed placeholder."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_DEFAULT_PLACEHOLDER = "***"

_DEFAULT_PATTERNS: List[str] = [
    r".*password.*",
    r".*secret.*",
    r".*token.*",
    r".*api[_-]?key.*",
    r".*private[_-]?key.*",
    r".*auth.*",
    r".*credential.*",
]


@dataclass
class CensorResult:
    config: Dict[str, str]
    censored_keys: List[str] = field(default_factory=list)
    placeholder: str = _DEFAULT_PLACEHOLDER

    def censor_count(self) -> int:
        return len(self.censored_keys)

    def has_censored(self) -> bool:
        return bool(self.censored_keys)

    def summary(self) -> str:
        if not self.has_censored():
            return "No keys censored."
        keys = ", ".join(sorted(self.censored_keys))
        return f"{self.censor_count()} key(s) censored: {keys}"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def censor_config(
    config: Dict[str, str],
    *,
    patterns: Optional[List[str]] = None,
    extra_keys: Optional[List[str]] = None,
    placeholder: str = _DEFAULT_PLACEHOLDER,
) -> CensorResult:
    """Return a copy of *config* with sensitive values replaced by *placeholder*.

    Matching is performed against each key using *patterns* (regex, case-insensitive).
    Additional explicit key names can be supplied via *extra_keys*.
    """
    compiled = _compile_patterns(patterns if patterns is not None else _DEFAULT_PATTERNS)
    explicit: set = set(extra_keys or [])

    result: Dict[str, str] = {}
    censored: List[str] = []

    for key, value in config.items():
        if key in explicit or any(p.fullmatch(key) for p in compiled):
            result[key] = placeholder
            censored.append(key)
        else:
            result[key] = value

    return CensorResult(config=result, censored_keys=censored, placeholder=placeholder)
