"""Encode config values using base64 or url encoding."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Literal

Encoding = Literal["base64", "url"]


@dataclass
class EncodeResult:
    encoded: Dict[str, str]
    skipped: list[str]
    encoding: str

    def encode_count(self) -> int:
        return len(self.encoded)

    def has_skipped(self) -> bool:
        return len(self.skipped) > 0

    def summary(self) -> str:
        parts = [f"encoded={self.encode_count()} ({self.encoding})"]
        if self.has_skipped():
            parts.append(f"skipped={len(self.skipped)}")
        return ", ".join(parts)


def _encode_value(value: str, encoding: Encoding) -> str | None:
    try:
        if encoding == "base64":
            return base64.b64encode(value.encode()).decode()
        elif encoding == "url":
            return urllib.parse.quote(value, safe="")
    except Exception:
        return None


def encode_config(
    config: Dict[str, str],
    encoding: Encoding = "base64",
    keys: list[str] | None = None,
) -> EncodeResult:
    """Encode config values. If keys is provided, only encode those keys."""
    encoded: Dict[str, str] = {}
    skipped: list[str] = []

    for key, value in config.items():
        if keys is not None and key not in keys:
            encoded[key] = value
            continue
        result = _encode_value(value, encoding)
        if result is None:
            skipped.append(key)
            encoded[key] = value
        else:
            encoded[key] = result

    return EncodeResult(encoded=encoded, skipped=skipped, encoding=encoding)
