from dataclasses import dataclass, field
from typing import Dict, List
import re


@dataclass
class LabelResult:
    config: Dict[str, str]
    labels: Dict[str, List[str]] = field(default_factory=dict)

    def label_count(self) -> int:
        return sum(len(v) for v in self.labels.values())

    def has_labels(self) -> bool:
        return self.label_count() > 0

    def summary(self) -> str:
        n = self.label_count()
        keys = len(self.labels)
        return f"{n} label(s) applied across {keys} key(s)"


_RULES: List[tuple] = [
    ("secret", re.compile(r"(SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE)", re.I)),
    ("database", re.compile(r"(DB_|DATABASE_|POSTGRES|MYSQL|MONGO)", re.I)),
    ("cache", re.compile(r"(REDIS|CACHE|MEMCACHE)", re.I)),
    ("feature", re.compile(r"(FEATURE_|FLAG_|ENABLE_|DISABLE_)", re.I)),
    ("network", re.compile(r"(HOST|PORT|URL|ENDPOINT|ADDR)", re.I)),
]


def label_config(
    config: Dict[str, str],
    extra_rules: Dict[str, str] | None = None,
) -> LabelResult:
    """Attach semantic labels to config keys based on naming patterns."""
    compiled_extra = [
        (label, re.compile(pattern, re.I))
        for label, pattern in (extra_rules or {}).items()
    ]
    all_rules = _RULES + compiled_extra

    labels: Dict[str, List[str]] = {}
    for key in config:
        matched = [label for label, rx in all_rules if rx.search(key)]
        if matched:
            labels[key] = matched

    return LabelResult(config=dict(config), labels=labels)
