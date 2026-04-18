"""Compute a deterministic digest (hash) of an env config for change detection."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DigestResult:
    config: Dict[str, str]
    digest: str
    algorithm: str = "sha256"
    key_count: int = 0
    previous_digest: Optional[str] = None
    changed: bool = False

    def summary(self) -> str:
        status = "changed" if self.changed else "unchanged"
        prev = f" (was {self.previous_digest[:12]}...)" if self.previous_digest and self.changed else ""
        return (
            f"Digest ({self.algorithm}): {self.digest[:16]}... "
            f"[{self.key_count} keys, {status}{prev}]"
        )


def _canonical_json(config: Dict[str, str]) -> bytes:
    """Produce a stable JSON bytes representation of config."""
    return json.dumps(config, sort_keys=True, separators=(",", ":")).encode()


def digest_config(
    config: Dict[str, str],
    algorithm: str = "sha256",
    previous_digest: Optional[str] = None,
) -> DigestResult:
    """Hash the given config dict and optionally compare to a previous digest."""
    if algorithm not in hashlib.algorithms_guaranteed:
        raise ValueError(f"Unsupported hash algorithm: {algorithm!r}")

    raw = _canonical_json(config)
    h = hashlib.new(algorithm, raw)
    digest = h.hexdigest()

    changed = previous_digest is not None and digest != previous_digest

    return DigestResult(
        config=config,
        digest=digest,
        algorithm=algorithm,
        key_count=len(config),
        previous_digest=previous_digest,
        changed=changed,
    )
