from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agent.planner import AgentPlanner
from backend.api.router_logic import Mode, decide_mode
from evals.metrics import precision_recall_f1
from evals.models import EvalResult, EvalSuiteResult, RoutingExample

logger = logging.getLogger(__name__)

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "routing_gold.jsonl"


def _load_dataset(path: str | Path | None = None) -> list[RoutingExample]:
    p = Path(path) if path else DATASET_PATH
    examples: list[RoutingExample] = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            examples.append(RoutingExample(**data))
    return examples


def _check_mode(query: str, expected_mode: str) -> tuple[bool, str]:
    predicted = decide_mode(query).value
    return predicted == expected_mode, predicted


def _check_tools(
    query: str, expected_tools: list[str]
) -> dict[str, Any]:
    planner = AgentPlanner()
    plan = planner.decompose(query)
    planned_tools = [step.get("tool", "") for step in plan]
    prf = precision_recall_f1(planned_tools, expected_tools)
    return {
        "planned_tools": planned_tools,
        "tools_matched": prf["f1"] >= 1.0,
        "precision": prf["precision"],
        "recall": prf["recall"],
        "f1": prf["f1"],
    }


def run_routing_eval(dataset_path: str | Path | None = None) -> EvalSuiteResult:
    examples = _load_dataset(dataset_path)
    results: list[EvalResult] = []

    for ex in examples:
        errors: list[str] = []
        mode_matched, predicted_mode = _check_mode(ex.query, ex.expected_mode)
        tool_info = _check_tools(ex.query, ex.expected_tools)

        if not mode_matched:
            errors.append(
                f"Expected mode '{ex.expected_mode}', got '{predicted_mode}'"
            )
        if not tool_info["tools_matched"]:
            errors.append(
                f"Expected tools {ex.expected_tools}, got {tool_info['planned_tools']} "
                f"(f1={tool_info['f1']})"
            )

        passed = mode_matched and tool_info["tools_matched"]
        score = 1.0 if passed else 0.0

        results.append(
            EvalResult(
                id=ex.id,
                passed=passed,
                score=score,
                errors=errors,
                metadata={
                    "query": ex.query,
                    "expected_mode": ex.expected_mode,
                    "predicted_mode": predicted_mode,
                    "mode_matched": mode_matched,
                    "planned_tools": tool_info["planned_tools"],
                    "expected_tools": ex.expected_tools,
                    "tools_f1": tool_info["f1"],
                },
            )
        )

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    final_score = passed_count / total if total else 0.0

    return EvalSuiteResult(
        suite_name="Routing & Planner Benchmark",
        total=total,
        passed=passed_count,
        failed=total - passed_count,
        score=round(final_score, 4),
        results=results,
    )
