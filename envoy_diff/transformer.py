"""Transformer module for applying key/value transformations to env configs."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    config: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def transform_count(self) -> int:
        return len(self.applied)

    def summary(self) -> str:
        if not self.applied:
            return "No transformations applied."
        parts = [f"Applied {self.transform_count} transformation(s): {', '.join(self.applied)}"]
        if self.skipped:
            parts.append(f"Skipped {len(self.skipped)} key(s): {', '.join(self.skipped)}")
        return " | ".join(parts)


def _uppercase_keys(config: Dict[str, str]) -> Dict[str, str]:
    return {k.upper(): v for k, v in config.items()}


def _strip_values(config: Dict[str, str]) -> Dict[str, str]:
    return {k: v.strip() for k, v in config.items()}


def _prefix_keys(config: Dict[str, str], prefix: str) -> Dict[str, str]:
    return {f"{prefix}{k}": v for k, v in config.items()}


_BUILTIN_TRANSFORMS: Dict[str, Callable[[Dict[str, str]], Dict[str, str]]] = {
    "uppercase_keys": _uppercase_keys,
    "strip_values": _strip_values,
}


def transform_config(
    config: Dict[str, str],
    transforms: List[str],
    prefix: Optional[str] = None,
) -> TransformResult:
    """Apply a list of named transforms to a config dict.

    Args:
        config: The input environment config.
        transforms: List of transform names to apply in order.
        prefix: Optional prefix to prepend to all keys after other transforms.

    Returns:
        TransformResult with the transformed config and metadata.
    """
    result = dict(config)
    applied: List[str] = []
    skipped: List[str] = []

    for name in transforms:
        if name in _BUILTIN_TRANSFORMS:
            result = _BUILTIN_TRANSFORMS[name](result)
            applied.append(name)
        else:
            skipped.append(name)

    if prefix:
        result = _prefix_keys(result, prefix)
        applied.append(f"prefix_keys({prefix!r})")

    return TransformResult(config=result, applied=applied, skipped=skipped)
