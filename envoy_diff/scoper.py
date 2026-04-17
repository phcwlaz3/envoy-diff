"""Scope filtering: restrict config keys to a named deployment scope."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope: str
    matched: Dict[str, str]
    excluded: Dict[str, str]
    prefixes: List[str] = field(default_factory=list)

    def matched_count(self) -> int:
        return len(self.matched)

    def excluded_count(self) -> int:
        return len(self.excluded)

    def summary(self) -> str:
        return (
            f"Scope '{self.scope}': {self.matched_count()} matched, "
            f"{self.excluded_count()} excluded"
        )


BUILTIN_SCOPES: Dict[str, List[str]] = {
    "database": ["DB_", "DATABASE_", "POSTGRES_", "MYSQL_"],
    "auth": ["AUTH_", "JWT_", "OAUTH_", "SECRET_"],
    "logging": ["LOG_", "LOGGING_", "SENTRY_"],
    "feature": ["FEATURE_", "FLAG_", "FF_"],
    "cache": ["CACHE_", "REDIS_", "MEMCACHE_"],
}


def scope_config(
    config: Dict[str, str],
    scope: str,
    extra_prefixes: Optional[List[str]] = None,
) -> ScopeResult:
    """Return only keys belonging to the named scope."""
    prefixes = list(BUILTIN_SCOPES.get(scope.lower(), []))
    if extra_prefixes:
        prefixes.extend(extra_prefixes)

    if not prefixes:
        # Unknown scope with no extra prefixes — match nothing
        return ScopeResult(
            scope=scope,
            matched={},
            excluded=dict(config),
            prefixes=prefixes,
        )

    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}
    for key, value in config.items():
        if any(key.upper().startswith(p.upper()) for p in prefixes):
            matched[key] = value
        else:
            excluded[key] = value

    return ScopeResult(scope=scope, matched=matched, excluded=excluded, prefixes=prefixes)
