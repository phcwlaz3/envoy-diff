"""Scorer module: assigns a numeric confidence score to a config diff."""

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_diff.differ import DiffResult

# Weights used when computing the overall score
_WEIGHT_ADDED = 1.0
_WEIGHT_REMOVED = 2.0  # removals are riskier than additions
_WEIGHT_CHANGED = 1.5
_MAX_SCORE = 100.0


@dataclass
class ScoreResult:
    """Holds the scoring outcome for a diff."""

    score: float
    risk_level: str
    breakdown: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Score: {self.score:.1f}/100  Risk: {self.risk_level}  "
            f"(+{self.breakdown.get('added', 0):.1f} "
            f"-{self.breakdown.get('removed', 0):.1f} "
            f"~{self.breakdown.get('changed', 0):.1f})"
        )


def _risk_level(score: float) -> str:
    if score >= 80:
        return "low"
    if score >= 50:
        return "medium"
    return "high"


def score_diff(diff: DiffResult, max_penalty: float = 40.0) -> ScoreResult:
    """Compute a 0-100 confidence score for *diff*.

    A perfect (empty) diff scores 100.  Each added, removed, or changed key
    contributes a weighted penalty, capped at *max_penalty* points total so
    that even very large diffs stay in the 0-100 range.
    """
    added_count = len(diff.added)
    removed_count = len(diff.removed)
    changed_count = len(diff.changed)

    raw_penalty = (
        added_count * _WEIGHT_ADDED
        + removed_count * _WEIGHT_REMOVED
        + changed_count * _WEIGHT_CHANGED
    )

    capped_penalty = min(raw_penalty, max_penalty)
    score = round(_MAX_SCORE - (capped_penalty / max_penalty) * _MAX_SCORE, 2)
    score = max(0.0, score)

    breakdown = {
        "added": round(added_count * _WEIGHT_ADDED, 2),
        "removed": round(removed_count * _WEIGHT_REMOVED, 2),
        "changed": round(changed_count * _WEIGHT_CHANGED, 2),
    }

    notes: List[str] = []
    if removed_count > added_count:
        notes.append("More keys removed than added — verify intentional deletions.")
    if changed_count > 5:
        notes.append(f"{changed_count} values changed — consider a staged rollout.")

    return ScoreResult(
        score=score,
        risk_level=_risk_level(score),
        breakdown=breakdown,
        notes=notes,
    )
