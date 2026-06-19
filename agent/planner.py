from __future__ import annotations

import logging
from typing import Any

from core.tracing import traced

logger = logging.getLogger(__name__)


class AgentPlanner:
    def __init__(self) -> None:
        self._plan: list[dict[str, Any]] = []

    @traced(agent="planner")
    def decompose(self, query: str) -> list[dict[str, Any]]:
        logger.info("Decomposing query: %s", query[:80])
        self._plan = self._build_plan(query)
        return self._plan

    def _build_plan(self, query: str) -> list[dict[str, Any]]:
        return [
            {
                "step": 1,
                "tool": "vector_search",
                "query": query,
                "description": "Retrieve relevant documents",
            },
            {
                "step": 2,
                "tool": "knowledge_graph",
                "query": query,
                "description": "Fetch graph relationships",
            },
        ]
