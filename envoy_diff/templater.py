"""Template rendering for env configs — fill a template with config values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


@dataclass
class TemplateResult:
    rendered: str
    resolved_keys: List[str] = field(default_factory=list)
    unresolved_keys: List[str] = field(default_factory=list)

    @property
    def resolution_count(self) -> int:
        return len(self.resolved_keys)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_keys)

    def summary(self) -> str:
        parts = [f"{self.resolution_count} placeholder(s) resolved"]
        if self.unresolved_keys:
            parts.append(f"{len(self.unresolved_keys)} unresolved: {', '.join(self.unresolved_keys)}")
        return "; ".join(parts)


def render_template(template: str, config: Dict[str, str]) -> TemplateResult:
    """Replace {{ KEY }} placeholders in *template* using values from *config*."""
    resolved: List[str] = []
    unresolved: List[str] = []
    seen_unresolved: set = set()

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in config:
            if key not in resolved:
                resolved.append(key)
            return config[key]
        if key not in seen_unresolved:
            unresolved.append(key)
            seen_unresolved.add(key)
        return match.group(0)

    rendered = _PLACEHOLDER_RE.sub(replacer, template)
    return TemplateResult(rendered=rendered, resolved_keys=resolved, unresolved_keys=unresolved)
