from __future__ import annotations

import importlib
import time
from typing import Any

from core.models import Evidence, ToolInput, ToolResult
from tools.base import BaseTool


class KnowledgeGraphTool(BaseTool):
    name = "knowledge_graph"
    description = "Query the Neo4j knowledge graph about satellite product relationships, using natural language translated to Cypher."
    input_schema: dict[str, Any] | None = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The natural language query about satellite data products and their relationships."},
        },
    }

    def run(self, input: ToolInput) -> ToolResult:
        start = time.perf_counter()
        query = input.query

        kg_module = self._load_kg_module()
        if kg_module is None:
            return ToolResult.from_error(
                self.name,
                "Missing required dependencies: langchain_neo4j, langchain_google_genai. Install them to use the knowledge graph tool.",
            )

        history = input.parameters.get("history")

        try:
            result = kg_module.ask_kg(question=query, history=history)
        except RuntimeError as e:
            return ToolResult.from_error(self.name, str(e))
        except Exception as e:
            return ToolResult.from_error(self.name, f"Knowledge graph query failed: {e}")

        evidence = [
            Evidence(
                content=result.get("answer", ""),
                source="knowledge_graph",
                metadata={
                    "cypher": result.get("cypher", ""),
                    "rows": result.get("rows", []),
                },
            )
        ]

        elapsed = (time.perf_counter() - start) * 1000
        return ToolResult.ok(
            self.name,
            evidence=evidence,
            answer=result.get("answer", ""),
            cypher=result.get("cypher", ""),
            rows=result.get("rows", []),
            latency_ms=round(elapsed, 1),
        )

    @staticmethod
    def _load_kg_module():
        try:
            return importlib.import_module("kg_pipeline.kg_nl_demo")
        except (ImportError, ModuleNotFoundError):
            return None
