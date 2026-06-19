from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from core.models import Evidence, ToolInput, ToolResult
from tools.base import BaseTool
from tools.registry import ToolRegistry

from evals.metrics import contains_all_keywords
from evals.models import AgentEvalExample, EvalResult, EvalSuiteResult

logger = logging.getLogger(__name__)

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "agent_gold.jsonl"


class FakeVectorSearchTool(BaseTool):
    name = "vector_search"
    description = "Fake vector search for evaluation"
    input_schema: dict[str, Any] | None = None

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.ok(
            tool_name=self.name,
            evidence=[
                Evidence(
                    content="INSAT-3D provides meteorological data at 1km resolution.",
                    source="fake_faiss/doc1",
                ),
                Evidence(
                    content="Oceansat-3 measures ocean color and sea surface temperature.",
                    source="fake_faiss/doc2",
                ),
            ],
            answer="FAKE: This is a synthetic vector search result for evaluation.",
        )


class FakeKnowledgeGraphTool(BaseTool):
    name = "knowledge_graph"
    description = "Fake knowledge graph for evaluation"
    input_schema: dict[str, Any] | None = None

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.ok(
            tool_name=self.name,
            evidence=[
                Evidence(
                    content="INSAT-3D is a satellite operated by ISRO for meteorology.",
                    source="fake_kg/INSAT-3D",
                ),
            ],
            answer="FAKE: This is a synthetic knowledge graph result for evaluation.",
        )


def _load_dataset(path: str | Path | None = None) -> list[AgentEvalExample]:
    p = Path(path) if path else DATASET_PATH
    examples: list[AgentEvalExample] = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            examples.append(AgentEvalExample(**data))
    return examples


def _build_fake_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(FakeVectorSearchTool())
    registry.register(FakeKnowledgeGraphTool())
    return registry


def run_agent_eval(dataset_path: str | Path | None = None) -> EvalSuiteResult:
    from agent.workflow import run_agent_query

    examples = _load_dataset(dataset_path)
    registry = _build_fake_registry()
    results: list[EvalResult] = []

    for ex in examples:
        errors: list[str] = []
        try:
            answer = run_agent_query(ex.query, registry=registry)
        except Exception as exc:
            results.append(
                EvalResult(
                    id=ex.id,
                    passed=False,
                    score=0.0,
                    errors=[f"Runtime error: {exc}"],
                    metadata={"query": ex.query, "crashed": True},
                )
            )
            continue

        passed = True
        score_parts: list[float] = []

        kw_ok = contains_all_keywords(answer, ex.expected_answer_keywords)
        if not kw_ok:
            errors.append(
                f"Answer missing expected keywords: {ex.expected_answer_keywords}"
            )
        score_parts.append(1.0 if kw_ok else 0.0)

        final_score = sum(score_parts) / len(score_parts) if score_parts else 0.0
        passed = kw_ok

        results.append(
            EvalResult(
                id=ex.id,
                passed=passed,
                score=round(final_score, 4),
                errors=errors,
                metadata={
                    "query": ex.query,
                    "expected_answer_keywords": ex.expected_answer_keywords,
                    "answer_preview": answer[:200],
                },
            )
        )

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    final_score = passed_count / total if total else 0.0

    return EvalSuiteResult(
        suite_name="Agent Workflow Benchmark",
        total=total,
        passed=passed_count,
        failed=total - passed_count,
        score=round(final_score, 4),
        results=results,
    )
