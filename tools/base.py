from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.models import ToolInput, ToolResult


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    input_schema: dict[str, Any] | None = None

    @abstractmethod
    def run(self, input: ToolInput) -> ToolResult:
        ...
