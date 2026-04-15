"""Interpolator: resolve ${VAR} references within env config values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}")


@dataclass
class InterpolationResult:
    config: Dict[str, str]
    resolved: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)

    @property
    def resolution_count(self) -> int:
        return len(self.resolved)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def summary(self) -> str:
        parts = [f"{self.resolution_count} reference(s) resolved"]
        if self.unresolved:
            keys = ", ".join(self.unresolved)
            parts.append(f"{len(self.unresolved)} unresolved: {keys}")
        return "; ".join(parts)


def _resolve_value(
    value: str,
    context: Dict[str, str],
    resolved: List[str],
    unresolved: List[str],
    owner_key: str,
) -> str:
    """Replace all ${VAR} tokens in *value* using *context*."""

    def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
        ref = match.group(1)
        if ref in context:
            resolved.append(owner_key)
            return context[ref]
        unresolved.append(owner_key)
        return match.group(0)  # leave token intact

    return _REF_PATTERN.sub(replacer, value)


def interpolate_config(
    config: Dict[str, str],
    extra_context: Optional[Dict[str, str]] = None,
) -> InterpolationResult:
    """Resolve ``${VAR}`` references in config values.

    Values are resolved against the config itself (self-referential) plus any
    *extra_context* supplied (e.g. OS environment variables).  The config
    dictionary is **not** mutated; a new dict is returned inside the result.

    Args:
        config: Mapping of env-var names to their raw values.
        extra_context: Optional additional variables available for resolution.

    Returns:
        :class:`InterpolationResult` with the resolved config and metadata.
    """
    context: Dict[str, str] = {**(extra_context or {}), **config}
    resolved: List[str] = []
    unresolved: List[str] = []

    new_config = {
        key: _resolve_value(value, context, resolved, unresolved, key)
        for key, value in config.items()
    }

    return InterpolationResult(
        config=new_config,
        resolved=list(dict.fromkeys(resolved)),   # deduplicate, preserve order
        unresolved=list(dict.fromkeys(unresolved)),
    )
