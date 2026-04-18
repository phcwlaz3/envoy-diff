from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AliasResult:
    config: Dict[str, str]
    aliases_added: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def alias_count(self) -> int:
        return len(self.aliases_added)

    def has_aliases(self) -> bool:
        return bool(self.aliases_added)

    def summary(self) -> str:
        if not self.aliases_added:
            return "No aliases applied."
        parts = [f"Applied {self.alias_count()} alias(es)."]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (source key missing).")
        return " ".join(parts)


def alias_config(
    config: Dict[str, str],
    aliases: Dict[str, str],
    overwrite: bool = False,
) -> AliasResult:
    """Create alias keys pointing to the same value as an existing key.

    Args:
        config: The source config dict.
        aliases: Mapping of {new_alias_key: existing_source_key}.
        overwrite: If True, overwrite an existing alias key. Default False.

    Returns:
        AliasResult with updated config and metadata.
    """
    result = dict(config)
    aliases_added: List[str] = []
    skipped: List[str] = []

    for alias_key, source_key in aliases.items():
        if source_key not in config:
            skipped.append(alias_key)
            continue
        if alias_key in result and not overwrite:
            skipped.append(alias_key)
            continue
        result[alias_key] = config[source_key]
        aliases_added.append(alias_key)

    return AliasResult(config=result, aliases_added=aliases_added, skipped=skipped)
