"""Clamp environment variable values to defined min/max length bounds."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ClampResult:
    config: Dict[str, str]
    clamped: List[Tuple[str, str, str]]  # (key, original, clamped)
    skipped: List[str] = field(default_factory=list)

    def clamp_count(self) -> int:
        return len(self.clamped)

    def has_clamped(self) -> bool:
        return len(self.clamped) > 0

    def summary(self) -> str:
        total = len(self.config)
        n = self.clamp_count()
        if n == 0:
            return f"{total} key(s) checked, none clamped."
        return f"{total} key(s) checked, {n} clamped to length bounds."


def _clamp_value(
    value: str,
    min_len: Optional[int],
    max_len: Optional[int],
    pad_char: str = " ",
) -> str:
    if max_len is not None and len(value) > max_len:
        return value[:max_len]
    if min_len is not None and len(value) < min_len:
        return value.ljust(min_len, pad_char)
    return value


def clamp_config(
    config: Dict[str, str],
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    keys: Optional[List[str]] = None,
    pad_char: str = " ",
) -> ClampResult:
    """Clamp string values to [min_len, max_len] bounds.

    Args:
        config:   The environment variable mapping to process.
        min_len:  Minimum value length; shorter values are right-padded.
        max_len:  Maximum value length; longer values are truncated.
        keys:     If provided, only clamp these specific keys.
        pad_char: Character used for left-padding when value is too short.

    Returns:
        ClampResult with the processed config and metadata.
    """
    if min_len is not None and max_len is not None and min_len > max_len:
        raise ValueError(f"min_len ({min_len}) must not exceed max_len ({max_len}).")

    result: Dict[str, str] = {}
    clamped: List[Tuple[str, str, str]] = []
    skipped: List[str] = []

    target_keys = set(keys) if keys else None

    for k, v in config.items():
        if target_keys is not None and k not in target_keys:
            result[k] = v
            continue

        new_v = _clamp_value(v, min_len, max_len, pad_char)
        result[k] = new_v
        if new_v != v:
            clamped.append((k, v, new_v))

    if target_keys:
        for k in target_keys:
            if k not in config:
                skipped.append(k)

    return ClampResult(config=result, clamped=clamped, skipped=skipped)
