from pathlib import Path

from evals.agent_eval import run_agent_eval

_HERE = Path(__file__).resolve().parent
_TEST_DATASET = _HERE.parent / "evals" / "datasets" / "agent_gold.jsonl"


def test_run_agent_eval_returns_suite_result():
    result = run_agent_eval(dataset_path=str(_TEST_DATASET))
    assert result.suite_name == "Agent Workflow Benchmark"
    assert result.total >= 10
    assert result.score >= 0.0


def test_run_agent_eval_all_results_have_ids():
    result = run_agent_eval(dataset_path=str(_TEST_DATASET))
    for r in result.results:
        assert r.id.startswith("a")


def test_run_agent_eval_no_external_services():
    """Must not require Neo4j, FAISS, Firebase, Gemini."""
    result = run_agent_eval(dataset_path=str(_TEST_DATASET))
    assert result.total > 0


def test_run_agent_eval_no_crashes():
    """Every example should complete without a runtime error."""
    result = run_agent_eval(dataset_path=str(_TEST_DATASET))
    for r in result.results:
        assert r.metadata.get("crashed") is not True
