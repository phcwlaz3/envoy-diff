"""Linter for environment variable configs — checks naming conventions and style."""

from dataclasses import dataclass, field
from typing import Dict, List
import re

SUSPECTED_PATTERNS = [
    (re.compile(r"^[a-z]"), "Key should be UPPER_SNAKE_CASE"),
    (re.compile(r"[^A-Z0-9_]"), "Key contains invalid characters"),
    (re.compile(r"^[0-9]"), "Key must not start with a digit"),
    (re.compile(r"__"), "Key contains consecutive underscores"),
]


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # 'warning' or 'error'


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        return (
            f"{len(self.issues)} issue(s): "
            f"{self.error_count} error(s), {self.warning_count} warning(s)."
        )


def _check_key(key: str) -> List[LintIssue]
    issues = []
    for pattern, message in SUSPECTED_PATTERNS:
        if pattern.search(key):
            severity = "error" if "invalid" in message or "digit" in message else "warning"
            issues.append(LintIssue(key=key, message=message, severity=severity))
            break  # report at most one issue per key
    if len(key) > 64:
        issues.append(LintIssue(key=key, message="Key exceeds 64 characters", severity="warning"))
    return issues


def lint_config(config: Dict[str, str]) -> LintResult:
    """Run all lint checks against the given config dict."""
    result = LintResult()
    for key in config:
        result.issues.extend(_check_key(key))
    return result
