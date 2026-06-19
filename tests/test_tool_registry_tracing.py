"""Tests for tool registry tracing — must pass without external services."""

from core.models import ToolInput, ToolResult
from core.tracing import RequestTrace, generate_trace_id
from tools.base import BaseTool
from tools.registry import ToolRegistry


class _DummyTool(BaseTool):
    name = "dummy"
    description = "Dummy tool for tracing tests"

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.ok(self.name, evidence=[], answer="ok")


class _FailingTool(BaseTool):
    name = "failing"
    description = "Tool that always fails"

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.from_error(self.name, "intentional failure")


class _CrashingTool(BaseTool):
    name = "crashing"
    description = "Tool that raises an exception"

    def run(self, input: ToolInput) -> ToolResult:
        raise ValueError("crash in tool")


def test_run_tool_with_trace_records_success():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    trace = RequestTrace(trace_id=generate_trace_id())

    result = registry.run_tool("dummy", "test query", trace=trace)
    assert result.success is True
    assert len(trace.tool_traces) == 1
    tt = trace.tool_traces[0]
    assert tt.tool_name == "dummy"
    assert tt.success is True
    assert tt.latency_ms is not None
    assert tt.evidence_count == 0


def test_run_tool_with_trace_records_failure():
    registry = ToolRegistry()
    registry.register(_FailingTool())
    trace = RequestTrace(trace_id=generate_trace_id())

    result = registry.run_tool("failing", "bad query", trace=trace)
    assert result.success is False
    assert len(trace.tool_traces) == 1
    tt = trace.tool_traces[0]
    assert tt.success is False
    assert tt.error == "intentional failure"


def test_run_tool_with_trace_records_crash():
    registry = ToolRegistry()
    registry.register(_CrashingTool())
    trace = RequestTrace(trace_id=generate_trace_id())

    result = registry.run_tool("crashing", "boom", trace=trace)
    assert result.success is False
    assert "crash in tool" in (result.error or "")
    assert len(trace.tool_traces) == 1
    tt = trace.tool_traces[0]
    assert tt.success is False
    assert "crash in tool" in (tt.error or "")


def test_run_tool_without_trace_still_works():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    result = registry.run_tool("dummy", "no trace")
    assert result.success is True


def test_trace_evidence_count():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    trace = RequestTrace(trace_id=generate_trace_id())
    registry.run_tool("dummy", "q", trace=trace)
    assert trace.tool_traces[0].evidence_count == 0
