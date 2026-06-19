from pathlib import Path

from evals.routing_eval import run_routing_eval

_HERE = Path(__file__).resolve().parent
_TEST_DATASET = _HERE.parent / "evals" / "datasets" / "routing_gold.jsonl"


def test_run_routing_eval_returns_suite_result():
    result = run_routing_eval(dataset_path=str(_TEST_DATASET))
    assert result.suite_name == "Routing & Planner Benchmark"
    assert result.total >= 20
    assert result.score >= 0.0


def test_run_routing_eval_all_results_have_ids():
    result = run_routing_eval(dataset_path=str(_TEST_DATASET))
    for r in result.results:
        assert r.id.startswith("r")


def test_run_routing_eval_no_external_services():
    """Must not require Neo4j, FAISS, Firebase, Gemini."""
    result = run_routing_eval(dataset_path=str(_TEST_DATASET))
    assert result.total > 0


def test_run_routing_eval_mode_matches_once():
    """At least some examples should match expected mode."""
    result = run_routing_eval(dataset_path=str(_TEST_DATASET))
    matched = sum(1 for r in result.results if r.metadata.get("mode_matched"))
    assert matched >= 1
