from __future__ import annotations

from typing import Any

from tools.base import BaseTool


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

    def run_tool(self, name: str, query: str, **kwargs: Any) -> Any:
        tool = self.get(name)
        from core.models import ToolInput

        return tool.run(ToolInput(query=query, parameters=kwargs))
