import pytest
from eval_pipeline.result_comparator import ResultComparator


@pytest.fixture
def comparator():
    return ResultComparator()


@pytest.fixture
def example_data():
    agent_output = {
        "root_cause": "The database connection pool was exhausted.",
        "causal_chain": ["app_requests_increase", "db_connections_exhausted"],
        "resolution": "Increase the database connection pool size.",
    }
    ground_truth = {
        "root_cause": "Database connection pool exhaustion.",
        "causal_graph": ["app_requests -> db_connections"],
        "resolution": "Adjust database connection limit.",
    }
    return agent_output, ground_truth


def test_root_cause_similarity(comparator, example_data):
    agent_output, ground_truth = example_data
    scores = comparator.compare(agent_output, ground_truth)
    assert 0.0 <= scores["rca_root_cause_score"] <= 1.0


def test_causal_chain_score(comparator, example_data):
    agent_output, ground_truth = example_data
    scores = comparator.compare(agent_output, ground_truth)
    assert 0.0 <= scores["rca_causal_chain_score"] <= 1.0


def test_resolution_correctness(comparator, example_data):
    agent_output, ground_truth = example_data
    scores = comparator.compare(agent_output, ground_truth)
    assert 0.0 <= scores["resolution_correctness_score"] <= 1.0
