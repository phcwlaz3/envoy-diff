import pytest
from envoy_diff.expander import expand_config, ExpandResult


@pytest.fixture
def sample_config():
    return {
        "HOSTS": "host1,host2,host3",
        "DB_URL": "postgres://localhost/mydb",
        "TAGS": "alpha,beta",
        "SINGLE": "only",
    }


def test_no_multi_value_returns_original():
    config = {"KEY": "value", "OTHER": "thing"}
    result = expand_config(config)
    assert result.config == config
    assert result.expand_count == 0


def test_multi_value_key_expanded(sample_config):
    result = expand_config(sample_config)
    assert "HOSTS_1" in result.config
    assert "HOSTS_2" in result.config
    assert "HOSTS_3" in result.config


def test_original_key_removed_after_expansion(sample_config):
    result = expand_config(sample_config)
    assert "HOSTS" not in result.config


def test_expanded_values_correct(sample_config):
    result = expand_config(sample_config)
    assert result.config["HOSTS_1"] == "host1"
    assert result.config["HOSTS_2"] == "host2"
    assert result.config["HOSTS_3"] == "host3"


def test_non_multi_value_preserved(sample_config):
    result = expand_config(sample_config)
    assert result.config["DB_URL"] == "postgres://localhost/mydb"
    assert result.config["SINGLE"] == "only"


def test_expand_count_correct(sample_config):
    result = expand_config(sample_config)
    assert result.expand_count == 2  # HOSTS and TAGS


def test_expanded_dict_lists_sub_keys(sample_config):
    result = expand_config(sample_config)
    assert result.expanded["TAGS"] == ["TAGS_1", "TAGS_2"]


def test_has_expanded_true(sample_config):
    result = expand_config(sample_config)
    assert result.has_expanded() is True


def test_has_expanded_false():
    result = expand_config({"K": "v"})
    assert result.has_expanded() is False


def test_custom_delimiter():
    config = {"PORTS": "8080|8081|8082"}
    result = expand_config(config, delimiter="|")
    assert result.config["PORTS_1"] == "8080"
    assert result.config["PORTS_3"] == "8082"


def test_custom_suffix_template():
    config = {"SERVERS": "a,b"}
    result = expand_config(config, suffix_template="[{i}]")
    assert "SERVERS[1]" in result.config
    assert "SERVERS[2]" in result.config


def test_summary_no_expansions():
    result = expand_config({"K": "v"})
    assert result.summary() == "No keys expanded."


def test_summary_with_expansions(sample_config):
    result = expand_config(sample_config)
    assert "2 key(s)" in result.summary()
