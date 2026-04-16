"""envoy-diff: CLI tool to diff and validate environment variable configs across deployment stages."""

__version__ = "0.1.0"
__author__ = "envoy-diff contributors"

from envoy_diff.loader import load_config, UnsupportedFormatError
from envoy_diff.differ import diff_configs

__all__ = ["load_config", "UnsupportedFormatError", "diff_configs", "get_version"]


def get_version() -> str:
    """Return the current version of envoy-diff.

    Returns:
        str: The version string (e.g. '0.1.0').
    """
    return __version__
