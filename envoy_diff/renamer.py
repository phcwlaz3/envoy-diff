"""Rename keys in an env config using a mapping or pattern rules."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import re


@dataclass
class RenameResult:
    config: Dict[str, str]
    renamed: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)
    skipped: List[str] = field(default_factory=list)

    def rename_count(self) -> int:
        return len(self.renamed)

    def has_renames(self) -> bool:
        return bool(self.renamed)

    def summary(self) -> str:
        if not self.renamed:
            return "No keys renamed."
        parts = [f"{old} -> {new}" for old, new in self.renamed]
        return f"Renamed {self.rename_count()} key(s): {', '.join(parts)}"


def rename_config(
    config: Dict[str, str],
    mapping: Dict[str, str] | None = None,
    pattern: str | None = None,
    replacement: str | None = None,
) -> RenameResult:
    """Rename keys via explicit mapping and/or regex pattern substitution."""
    result: Dict[str, str] = {}
    renamed: List[Tuple[str, str]] = []
    skipped: List[str] = []

    compiled = re.compile(pattern) if pattern else None

    for key, value in config.items():
        new_key = key

        if mapping and key in mapping:
            new_key = mapping[key]
        elif compiled and replacement is not None:
            new_key = compiled.sub(replacement, key)

        if new_key != key:
            if new_key in result:
                skipped.append(key)
                result[key] = value
                continue
            renamed.append((key, new_key))
        result[new_key] = value

    return RenameResult(config=result, renamed=renamed, skipped=skipped)
