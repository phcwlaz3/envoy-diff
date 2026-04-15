"""comparator.py — compare two snapshots or configs and produce a structured comparison report."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import diff_configs, DiffResult
from envoy_diff.validator import validate_config, ValidationResult


@dataclass
class ComparisonResult:
    """Holds the full result of comparing two named configs."""
    label_a: str
    label_b: str
    diff: DiffResult
    validation_a: ValidationResult
    validation_b: ValidationResult
    required_keys: List[str] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return bool(
            self.diff.added or self.diff.removed or self.diff.changed
        )

    @property
    def is_valid(self) -> bool:
        return bool(self.validation_a) and bool(self.validation_b)

    def summary(self) -> str:
        lines = [
            f"Comparison: {self.label_a!r} vs {self.label_b!r}",
            f"  Added keys   : {len(self.diff.added)}",
            f"  Removed keys : {len(self.diff.removed)}",
            f"  Changed keys : {len(self.diff.changed)}",
            f"  Validation A : {'OK' if self.validation_a else 'FAIL'}",
            f"  Validation B : {'OK' if self.validation_b else 'FAIL'}",
        ]
        if not self.validation_a:
            for issue in self.validation_a.errors + self.validation_a.warnings:
                lines.append(f"    [A] {issue}")
        if not self.validation_b:
            for issue in self.validation_b.errors + self.validation_b.warnings:
                lines.append(f"    [B] {issue}")
        return "\n".join(lines)


def compare_configs(
    config_a: Dict[str, str],
    config_b: Dict[str, str],
    label_a: str = "A",
    label_b: str = "B",
    required_keys: Optional[List[str]] = None,
) -> ComparisonResult:
    """Compare two config dicts and validate both sides.

    Args:
        config_a: First environment config dict.
        config_b: Second environment config dict.
        label_a: Human-readable label for the first config.
        label_b: Human-readable label for the second config.
        required_keys: Optional list of keys that must be present in both.

    Returns:
        A ComparisonResult with diff and validation details.
    """
    required = required_keys or []
    diff = diff_configs(config_a, config_b)
    val_a = validate_config(config_a, required_keys=required)
    val_b = validate_config(config_b, required_keys=required)
    return ComparisonResult(
        label_a=label_a,
        label_b=label_b,
        diff=diff,
        validation_a=val_a,
        validation_b=val_b,
        required_keys=required,
    )
