"""Environment variable config loader for envoy-diff.

Supports loading env configs from .env files, JSON, and YAML formats.
"""

import json
import os
from pathlib import Path
from typing import Dict


class UnsupportedFormatError(Exception):
    """Raised when the config file format is not supported."""


def load_env_file(path: str) -> Dict[str, str]:
    """Load environment variables from a .env file.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of environment variable key-value pairs.
    """
    env_vars: Dict[str, str] = {}
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(file_path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid format on line {line_num}: '{line}' (expected KEY=VALUE)"
                )
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                raise ValueError(f"Empty key on line {line_num}")
            env_vars[key] = value

    return env_vars


def load_json_file(path: str) -> Dict[str, str]:
    """Load environment variables from a JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(file_path, "r") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("JSON config must be a top-level object")

    return {str(k): str(v) for k, v in data.items()}


def load_config(path: str) -> Dict[str, str]:
    """Auto-detect format and load environment variables from a config file.

    Supported formats: .env, .json

    Args:
        path: Path to the config file.

    Returns:
        Dictionary of environment variable key-value pairs.
    """
    suffix = Path(path).suffix.lower()

    if suffix == ".json":
        return load_json_file(path)
    elif suffix in (".env", ""):
        return load_env_file(path)
    else:
        raise UnsupportedFormatError(
            f"Unsupported file format '{suffix}'. Supported: .env, .json"
        )
