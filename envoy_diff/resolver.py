"""Resolve environment variable values against a base config or system environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResolveResult:
    resolved: Dict[str, str]
    overrides: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    @property
    def override_count(self) -> int:
        return len(self.overrides)

    @property
    def missing_count(self) -> int:
        return len(self.missing)

    def summary(self) -> str:
        parts = [f"{len(self.resolved)} keys resolved"]
        if self.overrides:
            parts.append(f"{self.override_count} overridden from environment")
        if self.missing:
            parts.append(f"{self.missing_count} missing: {', '.join(self.missing)}")
        return "; ".join(parts)


def resolve_config(
    config: Dict[str, str],
    base: Optional[Dict[str, str]] = None,
    use_system_env: bool = False,
    required_keys: Optional[List[str]] = None,
) -> ResolveResult:
    """Resolve a config dict against a base config and/or system environment.

    Resolution priority (highest to lowest):
      1. System environment variables (if use_system_env=True)
      2. Provided config
      3. Base config fallback

    Args:
        config: The primary configuration dictionary to resolve.
        base: An optional base/default config to fall back to for missing keys.
        use_system_env: If True, system environment variables take highest priority.
        required_keys: Keys that must be present and non-empty in the resolved result.

    Returns:
        A ResolveResult containing the resolved values, any overridden keys, and
        any required keys that could not be resolved.
    """
    base = base or {}
    required_keys = required_keys or []

    resolved: Dict[str, str] = {}
    overrides: List[str] = []

    all_keys = set(base.keys()) | set(config.keys())

    for key in all_keys:
        if use_system_env and key in os.environ:
            resolved[key] = os.environ[key]
            if key in config and os.environ[key] != config.get(key):
                overrides.append(key)
        elif key in config:
            resolved[key] = config[key]
        else:
            resolved[key] = base[key]

    missing = [k for k in required_keys if k not in resolved or not resolved[k]]

    return ResolveResult(resolved=resolved, overrides=overrides, missing=missing)
