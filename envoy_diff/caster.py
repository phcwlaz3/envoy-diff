"""Type casting for environment variable values."""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class CastResult:
    config: Dict[str, Any]
    cast_keys: list = field(default_factory=list)
    failed_keys: list = field(default_factory=list)

    def cast_count(self) -> int:
        return len(self.cast_keys)

    def has_failures(self) -> bool:
        return len(self.failed_keys) > 0

    def summary(self) -> str:
        parts = [f"{self.cast_count()} key(s) cast"]
        if self.has_failures():
            parts.append(f"{len(self.failed_keys)} failure(s)")
        return ", ".join(parts)


def _try_cast(value: str, target_type: str) -> tuple:
    """Returns (cast_value, success)."""
    try:
        if target_type == "int":
            return int(value), True
        elif target_type == "float":
            return float(value), True
        elif target_type == "bool":
            if value.lower() in ("true", "1", "yes"):
                return True, True
            elif value.lower() in ("false", "0", "no"):
                return False, True
            raise ValueError(f"Cannot cast {value!r} to bool")
        elif target_type == "str":
            return str(value), True
        else:
            return value, False
    except (ValueError, AttributeError):
        return value, False


def cast_config(
    config: Dict[str, str],
    type_map: Dict[str, str],
) -> CastResult:
    """Cast config values to specified types based on key mapping.

    Args:
        config: flat key/value config dict.
        type_map: mapping of key -> target type (int, float, bool, str).

    Returns:
        CastResult with cast config and metadata.
    """
    result = {}
    cast_keys = []
    failed_keys = []

    for key, value in config.items():
        if key in type_map:
            cast_value, success = _try_cast(value, type_map[key])
            result[key] = cast_value
            if success:
                cast_keys.append(key)
            else:
                failed_keys.append(key)
        else:
            result[key] = value

    return CastResult(config=result, cast_keys=cast_keys, failed_keys=failed_keys)
