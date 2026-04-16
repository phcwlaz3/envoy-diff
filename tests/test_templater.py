"""Tests for envoy_diff.templater."""
import pytest
from envoy_diff.templater import render_template, TemplateResult


def test_no_placeholders_returns_template_unchanged():
    result = render_template("hello world", {"FOO": "bar"})
    assert result.rendered == "hello world"
    assert result.resolved_keys == []
    assert result.unresolved_keys == []


def test_single_placeholder_resolved():
    result = render_template("host={{ DB_HOST }}", {"DB_HOST": "localhost"})
    assert result.rendered == "host=localhost"
    assert "DB_HOST" in result.resolved_keys


def test_multiple_placeholders_resolved():
    tmpl = "{{ HOST }}:{{ PORT }}"
    result = render_template(tmpl, {"HOST": "db", "PORT": "5432"})
    assert result.rendered == "db:5432"
    assert result.resolution_count == 2


def test_unresolved_placeholder_left_intact():
    result = render_template("url={{ MISSING }}", {})
    assert result.rendered == "url={{ MISSING }}"
    assert "MISSING" in result.unresolved_keys
    assert result.has_unresolved is True


def test_mixed_resolved_and_unresolved():
    result = render_template("{{ A }}/{{ B }}", {"A": "foo"})
    assert result.rendered == "foo/{{ B }}"
    assert "A" in result.resolved_keys
    assert "B" in result.unresolved_keys


def test_duplicate_placeholder_counted_once():
    result = render_template("{{ X }} and {{ X }}", {"X": "val"})
    assert result.rendered == "val and val"
    assert result.resolved_keys.count("X") == 1


def test_duplicate_unresolved_counted_once():
    result = render_template("{{ Z }} then {{ Z }}", {})
    assert result.unresolved_keys.count("Z") == 1


def test_summary_all_resolved():
    result = render_template("{{ A }}", {"A": "1"})
    assert "1 placeholder(s) resolved" in result.summary()
    assert "unresolved" not in result.summary()


def test_summary_with_unresolved():
    result = render_template("{{ A }} {{ B }}", {"A": "1"})
    assert "unresolved" in result.summary()
    assert "B" in result.summary()


def test_whitespace_variants_in_placeholder():
    result = render_template("{{KEY}}", {"KEY": "v"})
    # strict match: no spaces — should still resolve
    assert result.rendered == "v"
