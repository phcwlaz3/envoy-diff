"""Mask specific config values by key pattern for safe display or export."""
from dataclasses import dataclass, field
from typing import Dict, List
import re

DEFAULT_MASK = "***"

DEFAULT_PATTERNS = [
    r".*password.*",
    r".*secret.*",
    r".*token.*",
    r".*api[_-]?key.*",
    r".*private[_-]?key.*",
    r".*auth.*",
    r".*credential.*",
]


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    def mask_count(self) -> int:
        return len(self.masked_keys)

    def has_masked(self) -> bool:
        return bool(self.masked_keys)

    def summary(self) -> str:
        if not self.has_masked():
            return "No keys masked."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{self.mask_count()} key(s) masked: {keys}"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def mask_config(
    config: Dict[str, str],
    patterns: List[str] = None,
    mask: str = DEFAULT_MASK,
    extra_keys: List[str] = None,
) -> MaskResult:
    compiled = _compile_patterns(patterns if patterns is not None else DEFAULT_PATTERNS)
    extra = {k.upper() for k in (extra_keys or [])}

    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in config.items():
        if key.upper() in extra or any(p.fullmatch(key) for p in compiled):
            masked[key] = mask
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(original=config, masked=masked, masked_keys=masked_keys)
