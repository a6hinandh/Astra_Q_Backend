from __future__ import annotations

import importlib
import time
from typing import Any

from core.models import Evidence, ToolInput, ToolResult
from tools.base import BaseTool


class VectorSearchTool(BaseTool):
    name = "vector_search"
    description = "Search the FAISS vector index for semantically relevant documents about satellite data products, then answer using Gemini."
    input_schema: dict[str, Any] | None = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The natural language query to search for."},
            "use_fallback": {"type": "boolean", "description": "Whether to use keyword fallback when semantic search returns no results."},
            "fallback_keyword": {"type": "string", "description": "Specific keyword for fallback search."},
        },
    }

    def run(self, input: ToolInput) -> ToolResult:
        start = time.perf_counter()
        query = input.query
        use_fallback = input.parameters.get("use_fallback", True)
        fallback_keyword = input.parameters.get("fallback_keyword")

        retrieve = self._load_retrieve_module()
        if retrieve is None:
            return ToolResult.from_error(self.name, "Missing required dependencies: langchain_huggingface, langchain_community, or google.generativeai.")

        history = input.parameters.get("history")

        try:
            result = retrieve.run_rag_pipeline(
                query=query,
                history=history,
                use_fallback=use_fallback,
                fallback_keyword=fallback_keyword,
            )
        except RuntimeError as e:
            return ToolResult.from_error(self.name, str(e))
        except Exception as e:
            return ToolResult.from_error(self.name, f"Vector search failed: {e}")

        evidence = [
            Evidence(
                content=s.get("content_preview", ""),
                source=s.get("source", "vector_store"),
                metadata={"page": s.get("page")} if s.get("page") else {},
            )
            for s in result.get("sources", [])
        ]

        elapsed = (time.perf_counter() - start) * 1000
        return ToolResult.ok(
            self.name,
            evidence=evidence,
            answer=result.get("answer", ""),
            latency_ms=round(elapsed, 1),
        )

    @staticmethod
    def _load_retrieve_module():
        try:
            return importlib.import_module("rag_pipeline.retrieve")
        except (ImportError, ModuleNotFoundError):
            return None
