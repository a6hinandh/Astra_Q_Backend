import tempfile
from pathlib import Path

from evals.agent_eval import run_agent_eval
from evals.report import generate_markdown_report
from evals.routing_eval import run_routing_eval

_HERE = Path(__file__).resolve().parent
_ROUTING_DATASET = _HERE.parent / "evals" / "datasets" / "routing_gold.jsonl"
_AGENT_DATASET = _HERE.parent / "evals" / "datasets" / "agent_gold.jsonl"


def test_generate_markdown_report_creates_file():
    routing = run_routing_eval(dataset_path=str(_ROUTING_DATASET))
    agent = run_agent_eval(dataset_path=str(_AGENT_DATASET))

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        tmp_path = f.name

    try:
        result_path = generate_markdown_report([routing, agent], tmp_path)
        assert Path(result_path).exists()
        content = Path(result_path).read_text(encoding="utf-8")
        assert "Vanta AI Evaluation Report" in content
        assert "Routing & Planner Benchmark" in content
        assert "Agent Workflow Benchmark" in content
        assert "Known Limitations" in content
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_generate_markdown_report_with_failed_examples():
    """Report should include failed examples section when there are failures."""
    routing = run_routing_eval(dataset_path=str(_ROUTING_DATASET))

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        tmp_path = f.name

    try:
        result_path = generate_markdown_report([routing], tmp_path)
        content = Path(result_path).read_text(encoding="utf-8")
        if routing.failed > 0:
            assert "Failed Examples" in content
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_eval_imports_without_external_services():
    """All eval modules should import without triggering external services."""
    from evals import models, metrics, grounding

    assert models.RoutingExample
    assert metrics.exact_match
    assert grounding.answer_has_source_overlap
