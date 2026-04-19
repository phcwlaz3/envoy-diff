"""Obscure config values by partially masking them, keeping a prefix visible."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re

DEFAULT_PATTERNS = [
    r"(?i)(secret|password|passwd|token|api_key|private_key|auth)",
]
DEFAULT_VISIBLE_CHARS = 4
MASK_CHAR = "*"
MASK_LENGTH = 6


@dataclass
class ObscureResult:
    original: Dict[str, str]
    obscured: Dict[str, str]
    obscured_keys: List[str] = field(default_factory=list)

    def obscure_count(self) -> int:
        return len(self.obscured_keys)

    def has_obscured(self) -> bool:
        return bool(self.obscured_keys)

    def summary(self) -> str:
        total = len(self.original)
        count = self.obscure_count()
        return f"Obscured {count}/{total} keys."


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def _obscure_value(value: str, visible_chars: int) -> str:
    if not value:
        return value
    visible = value[:visible_chars]
    return visible + MASK_CHAR * MASK_LENGTH


def obscure_config(
    config: Dict[str, str],
    patterns: List[str] | None = None,
    visible_chars: int = DEFAULT_VISIBLE_CHARS,
) -> ObscureResult:
    compiled = _compile_patterns(patterns if patterns is not None else DEFAULT_PATTERNS)
    obscured: Dict[str, str] = {}
    obscured_keys: List[str] = []

    for key, value in config.items():
        if any(p.search(key) for p in compiled):
            obscured[key] = _obscure_value(value, visible_chars)
            obscured_keys.append(key)
        else:
            obscured[key] = value

    return ObscureResult(original=config, obscured=obscured, obscured_keys=obscured_keys)
