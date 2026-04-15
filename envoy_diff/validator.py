"""Validation module for environment variable configs."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


def validate_keys_present(
    config: Dict[str, str],
    required_keys: Set[str],
) -> ValidationResult:
    """Ensure all required keys are present in the config."""
    missing = required_keys - config.keys()
    if missing:
        return ValidationResult(
            valid=False,
            errors=[f"Missing required key: '{k}'" for k in sorted(missing)],
        )
    return ValidationResult(valid=True)


def validate_no_empty_values(
    config: Dict[str, str],
    ignore_keys: Optional[Set[str]] = None,
) -> ValidationResult:
    """Warn about keys with empty string values."""
    ignore_keys = ignore_keys or set()
    warnings = [
        f"Key '{k}' has an empty value"
        for k, v in config.items()
        if v == "" and k not in ignore_keys
    ]
    return ValidationResult(valid=True, warnings=warnings)


def validate_config(
    config: Dict[str, str],
    required_keys: Optional[Set[str]] = None,
    ignore_empty_keys: Optional[Set[str]] = None,
) -> ValidationResult:
    """Run all validations against a config dict."""
    errors: List[str] = []
    warnings: List[str] = []

    if required_keys:
        result = validate_keys_present(config, required_keys)
        errors.extend(result.errors)

    empty_result = validate_no_empty_values(config, ignore_empty_keys)
    warnings.extend(empty_result.warnings)

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
