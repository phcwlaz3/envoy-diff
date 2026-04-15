"""Tests for envoy_diff.profiler."""

import pytest
from envoy_diff.profiler import profile_config, ProfileResult


def test_empty_config_scores_zero():
    result = profile_config({})
    assert result.score == 0
    assert result.grade() == "F"
    assert "empty" in result.notes[0].lower()


def test_clean_config_scores_high():
    config = {"HOST": "localhost", "PORT": "8080", "DEBUG": "false"}
    result = profile_config(config)
    assert result.score == 100
    assert result.grade() == "A"
    assert result.empty_count == 0
    assert result.suspicious_keys == []


def test_empty_values_reduce_score():
    config = {"HOST": "localhost", "PORT": "", "DB": ""}
    result = profile_config(config)
    assert result.empty_count == 2
    assert result.score < 100
    assert len(result.notes) >= 1


def test_suspicious_keys_reduce_score():
    config = {"API_KEY": "abc123", "HOST": "localhost"}
    result = profile_config(config)
    assert "API_KEY" in result.suspicious_keys
    assert result.score < 100


def test_suspicious_key_with_placeholder_not_flagged():
    config = {"API_KEY": "${SECRET_VALUE}", "HOST": "localhost"}
    result = profile_config(config)
    assert "API_KEY" not in result.suspicious_keys


def test_grade_boundaries():
    def make_result(score):
        return ProfileResult(score=score, total_keys=10, empty_count=0)

    assert make_result(95).grade() == "A"
    assert make_result(80).grade() == "B"
    assert make_result(65).grade() == "C"
    assert make_result(45).grade() == "D"
    assert make_result(20).grade() == "F"


def test_all_empty_values_score_low():
    config = {k: "" for k in ["A", "B", "C", "D", "E"]}
    result = profile_config(config)
    assert result.score <= 60
    assert result.empty_count == 5


def test_multiple_suspicious_keys_capped_penalty():
    config = {f"SECRET_{i}": f"val{i}" for i in range(10)}
    result = profile_config(config)
    assert result.score >= 0
    assert len(result.suspicious_keys) == 10
