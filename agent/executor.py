from __future__ import annotations

import logging
from typing import Any

from core.tracing import traced
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    @traced(agent="executor")
    def execute(self, plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Executing plan with %d steps", len(plan))
        results = []
        for step in plan:
            tool_name = step.get("tool", "")
            query = step.get("query", "")
            try:
                result = self.registry.run_tool(tool_name, query)
                results.append({
                    "step": step.get("step"),
                    "tool": tool_name,
                    "success": True,
                    "evidence": getattr(result, "evidence", None),
                })
            except Exception as exc:
                logger.error("Step %d failed: %s", step.get("step"), exc)
                results.append({
                    "step": step.get("step"),
                    "tool": tool_name,
                    "success": False,
                    "error": str(exc),
                })
        return results
