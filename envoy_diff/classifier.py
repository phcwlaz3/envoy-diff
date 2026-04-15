"""Classify environment variables by category based on key naming conventions."""

from dataclasses import dataclass, field
from typing import Dict, List

CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "database": ["DB_", "DATABASE_", "POSTGRES_", "MYSQL_", "MONGO_", "REDIS_"],
    "auth": ["AUTH_", "JWT_", "OAUTH_", "SECRET_", "TOKEN_", "API_KEY", "PASSWORD"],
    "network": ["HOST", "PORT", "URL", "ENDPOINT", "ADDR", "BIND_"],
    "logging": ["LOG_", "LOGGING_", "LOG"],
    "feature_flags": ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_"],
    "infrastructure": ["AWS_", "GCP_", "AZURE_", "K8S_", "KUBE_", "DOCKER_"],
}

UNCATEGORIZED = "uncategorized"


@dataclass
class ClassificationResult:
    categories: Dict[str, List[str]] = field(default_factory=dict)
    total: int = 0

    def category_count(self) -> int:
        return len([c for c, keys in self.categories.items() if keys])

    def summary(self) -> str:
        active = {
            cat: keys for cat, keys in self.categories.items() if keys
        }
        if not active:
            return "No keys classified."
        lines = [f"Classified {self.total} key(s) into {self.category_count()} category(s):"]
        for cat, keys in sorted(active.items()):
            lines.append(f"  {cat}: {len(keys)} key(s)")
        return "\n".join(lines)


def _match_category(key: str) -> str:
    upper_key = key.upper()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if upper_key.startswith(pattern) or upper_key == pattern.rstrip("_"):
                return category
    return UNCATEGORIZED


def classify_config(config: Dict[str, str]) -> ClassificationResult:
    """Classify all keys in config into named categories."""
    categories: Dict[str, List[str]] = {cat: [] for cat in CATEGORY_PATTERNS}
    categories[UNCATEGORIZED] = []

    for key in config:
        category = _match_category(key)
        categories[category].append(key)

    return ClassificationResult(categories=categories, total=len(config))
