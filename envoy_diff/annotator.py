"""Annotate config keys with arbitrary metadata labels."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnnotateResult:
    annotated: Dict[str, Dict[str, str]]  # key -> {original_value, annotation}
    skipped: List[str]

    def annotation_count(self) -> int:
        return len(self.annotated)

    def summary(self) -> str:
        total = len(self.annotated) + len(self.skipped)
        return (
            f"{self.annotation_count()} of {total} keys annotated, "
            f"{len(self.skipped)} skipped"
        )


def annotate_config(
    config: Dict[str, str],
    annotations: Dict[str, str],
    skip_missing: bool = True,
) -> AnnotateResult:
    """Attach annotation strings to matching config keys.

    Args:
        config: The environment config dict.
        annotations: Mapping of key -> annotation label to apply.
        skip_missing: If True, keys in annotations not present in config are
            silently skipped. If False, they are still recorded in skipped.

    Returns:
        AnnotateResult with annotated entries and skipped keys.
    """
    annotated: Dict[str, Dict[str, str]] = {}
    skipped: List[str] = []

    for key, label in annotations.items():
        if key in config:
            annotated[key] = {"value": config[key], "annotation": label}
        else:
            skipped.append(key)

    return AnnotateResult(annotated=annotated, skipped=skipped)
