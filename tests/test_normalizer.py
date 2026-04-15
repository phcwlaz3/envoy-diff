"""Tests for envoy_diff.normalizer."""

import pytest
from envoy_diff.normalizer import (
    NormalizeResult,
    normalize_config,
    _strip_quotes,
    _normalize_boolean,
)


# --- unit helpers ---

def test_strip_quotes_double():
    assert _strip_quotes('"hello"') == "hello"


def test_strip_quotes_single():
    assert _strip_quotes("'world'") == "world"


def test_strip_quotes_no_quotes():
    assert _strip_quotes("plain") == "plain"


def test_strip_quotes_mismatched():
    assert _strip_quotes("'mismatch\"") == "'mismatch\""


def test_normalize_boolean_true_variants():
    for val in ("true", "True", "TRUE", "yes", "Yes", "1", "on", "ON"):
        assert _normalize_boolean(val) == "true", f"failed for {val!r}"


def test_normalize_boolean_false_variants():
    for val in ("false", "False", "FALSE", "no", "No", "0", "off", "OFF"):
        assert _normalize_boolean(val) == "false", f"failed for {val!r}"


def test_normalize_boolean_passthrough():
    assert _normalize_boolean("maybe") == "maybe"


# --- normalize_config ---

def test_normalize_strips_whitespace():
    result = normalize_config({"KEY": "  value  "})
    assert result.normalized["KEY"] == "value"
    assert result.change_count == 1


def test_normalize_strips_quotes():
    result = normalize_config({"KEY": '"quoted"'})
    assert result.normalized["KEY"] == "quoted"


def test_normalize_booleans():
    result = normalize_config({"ENABLED": "yes", "DEBUG": "False"})
    assert result.normalized["ENABLED"] == "true"
    assert result.normalized["DEBUG"] == "false"


def test_normalize_no_changes():
    config = {"HOST": "localhost", "PORT": "8080"}
    result = normalize_config(config)
    assert result.change_count == 0
    assert result.normalized == config


def test_normalize_preserves_original():
    config = {"KEY": "  '  val  '  "}
    result = normalize_config(config)
    assert result.original["KEY"] == "  '  val  '  "


def test_normalize_summary_no_changes():
    result = normalize_config({"A": "clean"})
    assert result.summary() == "No normalization changes applied."


def test_normalize_summary_with_changes():
    result = normalize_config({"FLAG": "yes"})
    summary = result.summary()
    assert "Normalized 1 value" in summary
    assert "FLAG" in summary


def test_normalize_disable_strip_quotes():
    result = normalize_config({"K": '"quoted"'}, strip_quotes=False)
    assert result.normalized["K"] == '"quoted"'


def test_normalize_disable_booleans():
    result = normalize_config({"K": "yes"}, normalize_booleans=False)
    assert result.normalized["K"] == "yes"


def test_normalize_disable_whitespace():
    result = normalize_config({"K": "  val  "}, strip_whitespace=False)
    assert result.normalized["K"] == "  val  "
