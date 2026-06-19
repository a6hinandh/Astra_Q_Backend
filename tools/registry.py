from __future__ import annotations

import logging
import time
from typing import Any

from tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    pass


class ToolNotFoundError(ToolRegistryError):
    pass


class DuplicateToolError(ToolRegistryError):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise DuplicateToolError(
                f"Tool '{tool.name}' is already registered."
            )
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolNotFoundError(
                f"Tool '{name}' not found. Available: {list(self._tools.keys())}"
            )
        return self._tools[name]

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
        ]

    def run_tool(self, name: str, query: str, trace: Any = None, **kwargs: Any) -> Any:
        from core.models import ToolInput

        tool = self.get(name)
        start = time.perf_counter()
        input_summary = query[:80] if query else ""

        try:
            result = tool.run(ToolInput(query=query, parameters=kwargs))
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            result.latency_ms = elapsed_ms

            if trace is not None:
                from core.tracing import ToolTrace

                trace.add_tool_trace(
                    ToolTrace(
                        tool_name=name,
                        input_summary=input_summary,
                        success=result.success,
                        evidence_count=len(result.evidence),
                        latency_ms=elapsed_ms,
                        error=result.error,
                        metadata={
                            "error": result.error,
                        }
                        if result.error
                        else {},
                    )
                )

            logger.info(
                "Tool run: %s | success=%s | latency=%.0fms | evidence=%d | query_preview=%s",
                name,
                result.success,
                elapsed_ms,
                len(result.evidence),
                input_summary[:40],
            )
            return result

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            error_msg = f"{type(exc).__name__}: {exc}"

            if trace is not None:
                from core.tracing import ToolTrace

                trace.add_tool_trace(
                    ToolTrace(
                        tool_name=name,
                        input_summary=input_summary,
                        success=False,
                        evidence_count=0,
                        latency_ms=elapsed_ms,
                        error=error_msg,
                    )
                )

            logger.error(
                "Tool run failed: %s | latency=%.0fms | error=%s",
                name,
                elapsed_ms,
                error_msg,
            )
            from core.models import ToolResult

            return ToolResult.from_error(name, error_msg)
