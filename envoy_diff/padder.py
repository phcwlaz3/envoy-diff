"""Pad config values to a fixed width or align them for display."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PadResult:
    padded: Dict[str, str]
    pad_count: int
    width: int
    skipped: list = field(default_factory=list)

    def summary(self) -> str:
        parts = [f"{self.pad_count} value(s) padded to width {self.width}"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (already at or above width)")
        return "; ".join(parts)


def pad_count(result: PadResult) -> int:
    return result.pad_count


def has_padded(result: PadResult) -> bool:
    return result.pad_count > 0


def pad_config(
    config: Dict[str, str],
    width: int,
    fill_char: str = " ",
    align: str = "left",
    keys: Optional[list] = None,
) -> PadResult:
    """Pad string values in config to a minimum width.

    Args:
        config: The environment config dict.
        width: Minimum character width to pad values to.
        fill_char: Character used for padding (default space).
        align: 'left' (ljust) or 'right' (rjust).
        keys: Optional list of keys to pad; if None, all keys are processed.
    """
    if len(fill_char) != 1:
        raise ValueError("fill_char must be exactly one character")
    if align not in ("left", "right"):
        raise ValueError("align must be 'left' or 'right'")

    padded: Dict[str, str] = {}
    skipped: list = []
    pad_count_val = 0

    target_keys = keys if keys is not None else list(config.keys())

    for k, v in config.items():
        if k not in target_keys:
            padded[k] = v
            continue
        if len(v) >= width:
            padded[k] = v
            skipped.append(k)
        else:
            if align == "left":
                padded[k] = v.ljust(width, fill_char)
            else:
                padded[k] = v.rjust(width, fill_char)
            pad_count_val += 1

    return PadResult(
        padded=padded,
        pad_count=pad_count_val,
        width=width,
        skipped=skipped,
    )
