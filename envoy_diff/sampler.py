"""Sample a subset of keys from an env config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class SampleResult:
    sampled: Dict[str, str]
    total_keys: int
    sample_size: int
    seed: Optional[int]
    keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Sampled {self.sample_size} of {self.total_keys} keys"
            + (f" (seed={self.seed})" if self.seed is not None else "")
        )


def sample_count(result: SampleResult) -> int:
    return result.sample_size


def sample_config(
    config: Dict[str, str],
    n: Optional[int] = None,
    fraction: Optional[float] = None,
    seed: Optional[int] = None,
    prefix: Optional[str] = None,
) -> SampleResult:
    """Return a random sample of keys from *config*.

    Args:
        config:   Source key/value mapping.
        n:        Exact number of keys to sample.
        fraction: Fraction of keys to sample (0.0–1.0); ignored when *n* given.
        seed:     Random seed for reproducibility.
        prefix:   If set, only keys starting with this prefix are candidates.
    """
    candidates = {
        k: v for k, v in config.items()
        if prefix is None or k.startswith(prefix)
    }

    total = len(candidates)

    if n is None:
        frac = max(0.0, min(1.0, fraction if fraction is not None else 1.0))
        n = max(1, round(total * frac)) if total else 0

    n = min(n, total)

    rng = random.Random(seed)
    chosen_keys = rng.sample(sorted(candidates.keys()), n) if n else []
    sampled = {k: candidates[k] for k in chosen_keys}

    return SampleResult(
        sampled=sampled,
        total_keys=total,
        sample_size=len(sampled),
        seed=seed,
        keys=chosen_keys,
    )
