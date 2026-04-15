"""Apply a diff as a patch to produce an updated config."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import DiffResult


class PatchError(Exception):
    """Raised when a patch cannot be applied cleanly."""


@dataclass
class PatchResult:
    patched: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def apply_count(self) -> int:
        return len(self.applied)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        parts = [f"{self.apply_count} change(s) applied"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        return ", ".join(parts)


def patch_config(
    base: Dict[str, str],
    diff: DiffResult,
    *,
    strict: bool = False,
    ignore_removed: bool = False,
) -> PatchResult:
    """Apply *diff* onto *base* and return a PatchResult.

    Parameters
    ----------
    base:
        The config dict to patch.
    diff:
        A DiffResult produced by ``diff_configs``.
    strict:
        If True, raise PatchError on any conflict instead of recording it.
    ignore_removed:
        If True, keys present in diff.removed are left in the patched config.
    """
    patched = dict(base)
    applied: List[str] = []
    skipped: List[str] = []
    errors: List[str] = []

    # Apply additions
    for key, value in diff.added.items():
        if key in patched:
            msg = f"Cannot add '{key}': key already exists in base config"
            if strict:
                raise PatchError(msg)
            errors.append(msg)
        else:
            patched[key] = value
            applied.append(key)

    # Apply changes
    for key, (old_val, new_val) in diff.changed.items():
        if key not in patched:
            msg = f"Cannot change '{key}': key not found in base config"
            if strict:
                raise PatchError(msg)
            errors.append(msg)
        elif patched[key] != old_val:
            msg = (
                f"Conflict on '{key}': expected '{old_val}', "
                f"found '{patched[key]}'"
            )
            if strict:
                raise PatchError(msg)
            errors.append(msg)
        else:
            patched[key] = new_val
            applied.append(key)

    # Apply removals
    for key in diff.removed:
        if ignore_removed:
            skipped.append(key)
            continue
        if key not in patched:
            msg = f"Cannot remove '{key}': key not found in base config"
            if strict:
                raise PatchError(msg)
            errors.append(msg)
        else:
            del patched[key]
            applied.append(key)

    return PatchResult(
        patched=patched,
        applied=applied,
        skipped=skipped,
        errors=errors,
    )
