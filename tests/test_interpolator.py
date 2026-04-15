"""Tests for envoy_diff.interpolator."""

import pytest
from envoy_diff.interpolator import (
    InterpolationResult,
    interpolate_config,
)


# ---------------------------------------------------------------------------
# interpolate_config
# ---------------------------------------------------------------------------

def test_no_references_returns_config_unchanged():
    cfg = {"HOST": "localhost", "PORT": "8080"}
    result = interpolate_config(cfg)
    assert result.config == cfg
    assert result.resolved == []
    assert result.unresolved == []


def test_self_reference_resolved():
    cfg = {"BASE": "http://example.com", "URL": "${BASE}/api"}
    result = interpolate_config(cfg)
    assert result.config["URL"] == "http://example.com/api"
    assert "URL" in result.resolved


def test_multiple_references_in_one_value():
    cfg = {"SCHEME": "https", "HOST": "example.com", "FULL": "${SCHEME}://${HOST}"}
    result = interpolate_config(cfg)
    assert result.config["FULL"] == "https://example.com"


def test_unresolved_reference_left_intact():
    cfg = {"URL": "${MISSING}/path"}
    result = interpolate_config(cfg)
    assert result.config["URL"] == "${MISSING}/path"
    assert "URL" in result.unresolved


def test_extra_context_used_for_resolution():
    cfg = {"GREETING": "Hello, ${NAME}!"}
    result = interpolate_config(cfg, extra_context={"NAME": "World"})
    assert result.config["GREETING"] == "Hello, World!"
    assert "GREETING" in result.resolved


def test_config_takes_precedence_over_extra_context():
    """A key defined in config should shadow the same key in extra_context."""
    cfg = {"VAR": "from_config", "USE": "${VAR}"}
    result = interpolate_config(cfg, extra_context={"VAR": "from_extra"})
    assert result.config["USE"] == "from_config"


def test_original_config_not_mutated():
    cfg = {"A": "${B}", "B": "value"}
    original = dict(cfg)
    interpolate_config(cfg)
    assert cfg == original


def test_resolution_count_property():
    cfg = {"A": "${B}", "B": "hello", "C": "plain"}
    result = interpolate_config(cfg)
    assert result.resolution_count == 1


def test_has_unresolved_false_when_all_resolved():
    cfg = {"A": "${B}", "B": "ok"}
    result = interpolate_config(cfg)
    assert not result.has_unresolved


def test_has_unresolved_true_when_missing_ref():
    cfg = {"A": "${GHOST}"}
    result = interpolate_config(cfg)
    assert result.has_unresolved


def test_summary_no_unresolved():
    cfg = {"A": "${B}", "B": "val"}
    result = interpolate_config(cfg)
    assert "1 reference(s) resolved" in result.summary()
    assert "unresolved" not in result.summary()


def test_summary_with_unresolved():
    cfg = {"A": "${MISSING}"}
    result = interpolate_config(cfg)
    assert "unresolved" in result.summary()
    assert "MISSING" not in result.summary()  # key shown is the owner (A)
    assert "A" in result.summary()


def test_empty_config_returns_empty_result():
    result = interpolate_config({})
    assert result.config == {}
    assert result.resolved == []
    assert result.unresolved == []
