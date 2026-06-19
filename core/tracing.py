from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


def generate_trace_id() -> str:
    return uuid.uuid4().hex[:12]


class TraceStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class ToolTrace:
    tool_name: str
    input_summary: str = ""
    success: bool = True
    evidence_count: int = 0
    latency_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestTrace:
    trace_id: str
    query: str = ""
    selected_mode: str = ""
    user_id: str = ""
    thread_id: str = ""
    started_at: float | None = None
    ended_at: float | None = None
    latency_ms: float | None = None
    status: TraceStatus = TraceStatus.SUCCESS
    final_answer_preview: str = ""
    error: str | None = None
    tool_traces: list[ToolTrace] = field(default_factory=list)

    def add_tool_trace(self, tool_trace: ToolTrace) -> None:
        self.tool_traces.append(tool_trace)

    def finalize(self, *, answer: str = "", error: str | None = None) -> None:
        self.ended_at = time.time()
        self.latency_ms = round((self.ended_at - (self.started_at or self.ended_at)) * 1000, 1)
        self.final_answer_preview = answer[:200] if answer else ""
        if error:
            self.error = error
            self.status = TraceStatus.ERROR
        elif any(not tt.success for tt in self.tool_traces):
            self.status = TraceStatus.PARTIAL
        else:
            self.status = TraceStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "query_preview": self.query[:100] if self.query else "",
            "selected_mode": self.selected_mode,
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "latency_ms": self.latency_ms,
            "status": self.status.value,
            "final_answer_preview": self.final_answer_preview,
            "error": self.error,
            "tool_traces": [
                {
                    "tool_name": tt.tool_name,
                    "input_summary": tt.input_summary[:80],
                    "success": tt.success,
                    "evidence_count": tt.evidence_count,
                    "latency_ms": tt.latency_ms,
                    "error": tt.error,
                }
                for tt in self.tool_traces
            ],
        }


class TraceStore:
    def __init__(self, max_size: int = 500) -> None:
        self._traces: dict[str, RequestTrace] = {}
        self._max_size = max_size
        self._insertion_order: list[str] = []

    def add(self, trace: RequestTrace) -> None:
        self._traces[trace.trace_id] = trace
        self._insertion_order.append(trace.trace_id)
        if len(self._insertion_order) > self._max_size:
            oldest = self._insertion_order.pop(0)
            self._traces.pop(oldest, None)

    def get(self, trace_id: str) -> RequestTrace | None:
        return self._traces.get(trace_id)

    def list_recent(self, limit: int = 20) -> list[RequestTrace]:
        recent_ids = self._insertion_order[-limit:]
        return [self._traces[tid] for tid in recent_ids if tid in self._traces]

    def clear(self) -> None:
        self._traces.clear()
        self._insertion_order.clear()

    def __len__(self) -> int:
        return len(self._traces)


trace_store = TraceStore()
