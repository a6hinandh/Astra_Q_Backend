from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evals.models import EvalSuiteResult

logger = logging.getLogger(__name__)


def _suite_table_row(result: EvalSuiteResult) -> list[str]:
    pct = round(result.score * 100, 1)
    return [
        result.suite_name,
        str(result.total),
        str(result.passed),
        str(result.failed),
        f"{pct}%",
    ]


def _failed_examples(results: list[EvalSuiteResult]) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    for suite in results:
        for r in suite.results:
            if not r.passed:
                failed.append(
                    {
                        "suite": suite.suite_name,
                        "id": r.id,
                        "errors": r.errors,
                        "metadata": r.metadata,
                    }
                )
    return failed


def generate_markdown_report(
    results: list[EvalSuiteResult], output_path: str | Path
) -> Path:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("# Vanta AI Evaluation Report")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append("")
    lines.append("## Suite Summary")
    lines.append("")
    lines.append("| Suite | Total | Passed | Failed | Score |")
    lines.append("|-------|-------|--------|--------|-------|")
    for suite_result in results:
        lines.append("| " + " | ".join(_suite_table_row(suite_result)) + " |")

    total_all = sum(s.total for s in results)
    passed_all = sum(s.passed for s in results)
    avg_score = (
        round(sum(s.score for s in results) / len(results), 4) if results else 0.0
    )
    lines.append("")
    lines.append(f"**Overall:** {passed_all}/{total_all} passed, average score **{round(avg_score * 100, 1)}%**")
    lines.append("")

    failed_exs = _failed_examples(results)
    if failed_exs:
        lines.append("## Failed Examples")
        lines.append("")
        for fe in failed_exs:
            lines.append(f"### {fe['suite']} — `{fe['id']}`")
            lines.append("")
            for err in fe["errors"]:
                lines.append(f"- {err}")
            lines.append("")

    lines.append("## Known Limitations")
    lines.append("")
    lines.append(
        "- Benchmarks are lightweight and run locally without external services."
    )
    lines.append(
        "- Routing accuracy reflects the current heuristic-based router (`backend/api/router_logic.py`)."
    )
    lines.append(
        "- Tool selection accuracy tests the Planner's `decompose()` method, which currently returns a fixed plan."
    )
    lines.append(
        "- Agent workflow benchmarks use fake tools that return controlled synthetic data."
    )
    lines.append("- No live retrieval quality benchmark (MRR over real indexed documents) yet.")
    lines.append("- No full hallucination or grounding evaluator yet.")
    lines.append("- Trace quality checks are not yet benchmarked.")
    lines.append("")
    lines.append("## Future Work")
    lines.append("")
    lines.append("- Retrieval MRR evaluation over real FAISS index")
    lines.append("- Grounded answer evaluation with citation overlap scoring")
    lines.append("- Trace quality benchmarks (latency, completeness)")
    lines.append("- Multi-turn conversation evaluation")
    lines.append("- Integration with CI pipeline")

    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Report written to %s", p.resolve())
    return p
