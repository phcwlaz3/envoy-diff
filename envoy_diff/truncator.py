"""Truncate long environment variable values for display purposes."""
from dataclasses import dataclass, field
from typing import Dict

DEFAULT_MAX_LENGTH = 64
TRUNCATION_MARKER = "..."


@dataclass
class TruncateResult:
    original: Dict[str, str]
    truncated: Dict[str, str]
    truncated_keys: list = field(default_factory=list)

    def truncation_count(self) -> int:
        return len(self.truncated_keys)

    def has_truncations(self) -> bool:
        return len(self.truncated_keys) > 0

    def summary(self) -> str:
        count = self.truncation_count()
        if count == 0:
            return "No values truncated."
        return f"{count} value(s) truncated to max length."


def _truncate_value(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    keep = max_length - len(TRUNCATION_MARKER)
    return value[:keep] + TRUNCATION_MARKER


def truncate_config(
    config: Dict[str, str],
    max_length: int = DEFAULT_MAX_LENGTH,
    keys: list = None,
) -> TruncateResult:
    """Return a new config with long values truncated.

    Args:
        config: The env config dict to process.
        max_length: Maximum allowed value length before truncation.
        keys: Optional list of specific keys to truncate. If None, all keys are considered.
    """
    truncated = {}
    truncated_keys = []

    for k, v in config.items():
        if keys is not None and k not in keys:
            truncated[k] = v
            continue
        new_v = _truncate_value(str(v), max_length)
        truncated[k] = new_v
        if new_v != v:
            truncated_keys.append(k)

    return TruncateResult(
        original=config,
        truncated=truncated,
        truncated_keys=truncated_keys,
    )
