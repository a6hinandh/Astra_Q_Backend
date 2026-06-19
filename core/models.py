from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Evidence:
    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float | None = None


@dataclass
class ToolInput:
    query: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    evidence: list[Evidence] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None

    @classmethod
    def from_error(cls, tool_name: str, error: str) -> ToolResult:
        return cls(tool_name=tool_name, success=False, error=error)

    @classmethod
    def ok(cls, tool_name: str, evidence: list[Evidence], **metadata: Any) -> ToolResult:
        return cls(tool_name=tool_name, success=True, evidence=evidence, metadata=metadata)


@dataclass
class ToolCall:
    tool_name: str
    input: ToolInput
    call_id: str = ""


class ToolError(Exception):
    pass
