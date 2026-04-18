from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CoerceResult:
    config: dict[str, Any]
    coerced: dict[str, str]  # key -> target type name
    failures: dict[str, str]  # key -> error message

    def coerce_count(self) -> int:
        return len(self.coerced)

    def has_failures(self) -> bool:
        return bool(self.failures)

    def summary(self) -> str:
        parts = [f"{self.coerce_count()} key(s) coerced"]
        if self.failures:
            parts.append(f"{len(self.failures)} failure(s)")
        return ", ".join(parts)


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _coerce_value(value: str, target: str) -> Any:
    if target == "int":
        return int(value)
    if target == "float":
        return float(value)
    if target == "bool":
        low = value.strip().lower()
        if low in _BOOL_TRUE:
            return True
        if low in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot coerce {value!r} to bool")
    if target == "str":
        return str(value)
    raise ValueError(f"Unknown target type: {target!r}")


def coerce_config(
    config: dict[str, str],
    rules: dict[str, str],
) -> CoerceResult:
    """Coerce config values to specified types according to rules.

    Args:
        config: mapping of env var key -> string value
        rules: mapping of key -> target type ("int", "float", "bool", "str")

    Returns:
        CoerceResult with updated config, coerced keys, and any failures.
    """
    result: dict[str, Any] = dict(config)
    coerced: dict[str, str] = {}
    failures: dict[str, str] = {}

    for key, target in rules.items():
        if key not in config:
            continue
        try:
            result[key] = _coerce_value(config[key], target)
            coerced[key] = target
        except (ValueError, TypeError) as exc:
            failures[key] = str(exc)

    return CoerceResult(config=result, coerced=coerced, failures=failures)
