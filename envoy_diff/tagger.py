"""Tag environment config keys with user-defined labels."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TagResult:
    tagged: Dict[str, List[str]]  # key -> list of tags
    untagged: Set[str]

    def tag_count(self) -> int:
        return sum(len(tags) for tags in self.tagged.values())

    def summary(self) -> str:
        total_keys = len(self.tagged) + len(self.untagged)
        tagged_keys = len(self.tagged)
        return (
            f"{tagged_keys}/{total_keys} keys tagged "
            f"({self.tag_count()} total tag assignments)"
        )


def tag_config(
    config: Dict[str, str],
    tag_rules: Dict[str, List[str]],
) -> TagResult:
    """Apply tag_rules to config keys.

    tag_rules maps a tag name to a list of key substrings that trigger it.
    Example: {"secret": ["PASSWORD", "SECRET", "TOKEN"]}
    """
    tagged: Dict[str, List[str]] = {}
    untagged: Set[str] = set()

    for key in config:
        key_upper = key.upper()
        assigned: List[str] = []
        for tag, patterns in tag_rules.items():
            if any(p.upper() in key_upper for p in patterns):
                assigned.append(tag)
        if assigned:
            tagged[key] = assigned
        else:
            untagged.add(key)

    return TagResult(tagged=tagged, untagged=untagged)
