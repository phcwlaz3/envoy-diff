"""Thin re-export so commands package exposes diff_cmd."""
from envoy_diff.differ_cmd import add_diff_subparsers, run_diff_command

__all__ = ["add_diff_subparsers", "run_diff_command"]
