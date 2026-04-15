"""envoy-diff: CLI tool to diff and validate environment variable configs across deployment stages."""

__version__ = "0.1.0"
__author__ = "envoy-diff contributors"

from envoy_diff.loader import load_config, UnsupportedFormatError

__all__ = ["load_config", "UnsupportedFormatError"]
