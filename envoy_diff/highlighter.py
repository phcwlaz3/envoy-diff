"""Highlight changed keys in a config based on a reference config."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class HighlightResult:
    highlighted: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)
    added_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def highlight_count(self) -> int:
        return len(self.changed_keys) + len(self.added_keys) + len(self.removed_keys)

    def has_highlights(self) -> bool:
        return self.highlight_count() > 0

    def summary(self) -> str:
        if not self.has_highlights():
            return "No differences highlighted."
        parts = []
        if self.added_keys:
            parts.append(f"{len(self.added_keys)} added")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        if self.changed_keys:
            parts.append(f"{len(self.changed_keys)} changed")
        return "Highlighted: " + ", ".join(parts) + "."

    def filter_by_status(self, status: str) -> Dict[str, str]:
        """Return only highlighted entries matching the given status marker.

        Args:
            status: One of 'added', 'removed', 'changed', or 'unchanged'.

        Returns:
            A dict of key/value pairs whose highlighted values carry the
            corresponding marker prefix.
        """
        marker_map = {
            "added": ADDED_MARKER,
            "removed": REMOVED_MARKER,
            "changed": CHANGED_MARKER,
            "unchanged": UNCHANGED_MARKER,
        }
        if status not in marker_map:
            raise ValueError(
                f"Invalid status {status!r}. Expected one of: {list(marker_map)}"
            )
        prefix = marker_map[status]
        return {k: v for k, v in self.highlighted.items() if v.startswith(prefix)}


ADDED_MARKER = "[+]"
REMOVED_MARKER = "[-]"
CHANGED_MARKER = "[~]"
UNCHANGED_MARKER = "[ ]"


def highlight_config(
    config: Dict[str, str],
    reference: Optional[Dict[str, str]] = None,
) -> HighlightResult:
    """Return a copy of config with marker prefixes indicating change status."""
    if reference is None:
        reference = {}

    highlighted: Dict[str, str] = {}
    changed_keys: List[str] = []
    added_keys: List[str] = []
    removed_keys: List[str] = []

    for key, value in config.items():
        if key not in reference:
            highlighted[key] = f"{ADDED_MARKER} {value}"
            added_keys.append(key)
        elif reference[key] != value:
            highlighted[key] = f"{CHANGED_MARKER} {value}"
            changed_keys.append(key)
        else:
            highlighted[key] = f"{UNCHANGED_MARKER} {value}"

    for key, value in reference.items():
        if key not in config:
            highlighted[key] = f"{REMOVED_MARKER} {value}"
            removed_keys.append(key)

    return HighlightResult(
        highlighted=highlighted,
        changed_keys=sorted(changed_keys),
        added_keys=sorted(added_keys),
        removed_keys=sorted(removed_keys),
    )
