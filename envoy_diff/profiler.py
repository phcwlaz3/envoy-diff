"""Profile and score environment configs based on completeness and hygiene."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProfileResult:
    score: int  # 0-100
    total_keys: int
    empty_count: int
    suspicious_keys: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def grade(self) -> str:
        if self.score >= 90:
            return "A"
        elif self.score >= 75:
            return "B"
        elif self.score >= 60:
            return "C"
        elif self.score >= 40:
            return "D"
        return "F"


_SUSPICIOUS_PATTERNS = ["password", "secret", "token", "key", "api_key", "auth"]


def _find_suspicious_keys(config: Dict[str, str]) -> List[str]:
    """Return keys that look like secrets but have plaintext-looking values."""
    found = []
    for k, v in config.items():
        lower_key = k.lower()
        if any(pat in lower_key for pat in _SUSPICIOUS_PATTERNS):
            if v and not v.startswith("${") and len(v) < 64:
                found.append(k)
    return found


def profile_config(config: Dict[str, str]) -> ProfileResult:
    """Analyse a config dict and return a ProfileResult with a score."""
    total = len(config)
    if total == 0:
        return ProfileResult(score=0, total_keys=0, empty_count=0,
                             notes=["Config is empty."])

    empty_keys = [k for k, v in config.items() if v == ""]
    suspicious = _find_suspicious_keys(config)
    notes: List[str] = []

    penalty = 0
    empty_ratio = len(empty_keys) / total
    penalty += int(empty_ratio * 40)
    if empty_keys:
        notes.append(f"{len(empty_keys)} empty value(s) found: {', '.join(empty_keys[:5])}.")

    penalty += min(len(suspicious) * 5, 30)
    if suspicious:
        notes.append(f"{len(suspicious)} potentially exposed secret key(s): {', '.join(suspicious[:5])}.")

    score = max(0, 100 - penalty)
    return ProfileResult(
        score=score,
        total_keys=total,
        empty_count=len(empty_keys),
        suspicious_keys=suspicious,
        notes=notes,
    )
