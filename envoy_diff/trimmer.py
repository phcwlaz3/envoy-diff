from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimResult:
    config: Dict[str, str]
    trimmed_keys: List[str] = field(default_factory=list)

    def trim_count(self) -> int:
        return len(self.trimmed_keys)

    def has_trimmed(self) -> bool:
        return len(self.trimmed_keys) > 0

    def summary(self) -> str:
        if not self.trimmed_keys:
            return "No values trimmed."
        return f"{self.trim_count()} value(s) trimmed: {', '.join(self.trimmed_keys)}"


def trim_config(
    config: Dict[str, str],
    keys: List[str] = None,
    strip_chars: str = None,
) -> TrimResult:
    """Strip leading/trailing whitespace (or custom chars) from config values.

    Args:
        config: The input config dictionary.
        keys: If provided, only trim values for these keys.
        strip_chars: Characters to strip. Defaults to whitespace.
    """
    result: Dict[str, str] = {}
    trimmed_keys: List[str] = []

    for k, v in config.items():
        if keys is not None and k not in keys:
            result[k] = v
            continue

        if isinstance(v, str):
            stripped = v.strip(strip_chars) if strip_chars is not None else v.strip()
            if stripped != v:
                trimmed_keys.append(k)
            result[k] = stripped
        else:
            result[k] = v

    return TrimResult(config=result, trimmed_keys=trimmed_keys)
