"""Tests focused on text rendering of the diff command."""
import pytest
from argparse import Namespace
from envoy_diff.commands.diff_cmd import run_diff_command


@pytest.fixture
def base(tmp_path):
    f = tmp_path / "a.env"
    f.write_text("KEEP=same\nOLD_KEY=gone\nCHANGED=before\n")
    return str(f)


@pytest.fixture
def head(tmp_path):
    f = tmp_path / "b.env"
    f.write_text("KEEP=same\nNEW_KEY=arrived\nCHANGED=after\n")
    return str(f)


def _args(base, head, score=False):
    return Namespace(base=base, head=head, format="text", score=score)


def test_text_added_key_prefixed_plus(base, head, capsys):
    run_diff_command(_args(base, head))
    out = capsys.readouterr().out
    assert "+ NEW_KEY=arrived" in out


def test_text_removed_key_prefixed_minus(base, head, capsys):
    run_diff_command(_args(base, head))
    out = capsys.readouterr().out
    assert "- OLD_KEY" in out


def test_text_changed_key_prefixed_tilde(base, head, capsys):
    run_diff_command(_args(base, head))
    out = capsys.readouterr().out
    assert "~ CHANGED" in out
    assert "before" in out
    assert "after" in out


def test_text_no_diff_message(base, capsys):
    run_diff_command(_args(base, base))
    out = capsys.readouterr().out
    assert "No differences" in out


def test_text_score_line_present(base, head, capsys):
    run_diff_command(_args(base, head, score=True))
    out = capsys.readouterr().out
    assert "Risk score" in out
