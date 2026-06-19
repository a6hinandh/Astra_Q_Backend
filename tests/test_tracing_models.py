"""Tests for core/tracing.py models — must pass without external services."""

import time
from core.tracing import (
    RequestTrace,
    ToolTrace,
    TraceStatus,
    generate_trace_id,
)


def test_generate_trace_id():
    tid = generate_trace_id()
    assert isinstance(tid, str)
    assert len(tid) == 12


def test_generate_trace_id_unique():
    ids = {generate_trace_id() for _ in range(100)}
    assert len(ids) == 100


def test_tool_trace_defaults():
    tt = ToolTrace(tool_name="vector_search")
    assert tt.tool_name == "vector_search"
    assert tt.input_summary == ""
    assert tt.success is True
    assert tt.evidence_count == 0
    assert tt.latency_ms is None
    assert tt.error is None
    assert tt.metadata == {}


def test_tool_trace_with_all_fields():
    tt = ToolTrace(
        tool_name="kg",
        input_summary="which products",
        success=False,
        evidence_count=0,
        latency_ms=150.5,
        error="Neo4j connection failed",
        metadata={"key": "val"},
    )
    assert tt.latency_ms == 150.5
    assert tt.error == "Neo4j connection failed"


def test_request_trace_defaults():
    rt = RequestTrace(trace_id="abc123")
    assert rt.trace_id == "abc123"
    assert rt.status == TraceStatus.SUCCESS
    assert rt.tool_traces == []


def test_request_trace_add_tool_trace():
    rt = RequestTrace(trace_id="t1", started_at=time.time())
    tt = ToolTrace(tool_name="vs")
    rt.add_tool_trace(tt)
    assert len(rt.tool_traces) == 1
    assert rt.tool_traces[0].tool_name == "vs"


def test_request_trace_finalize_success():
    rt = RequestTrace(trace_id="t1", started_at=time.time() - 0.5)
    rt.add_tool_trace(ToolTrace(tool_name="vs", success=True))
    rt.finalize(answer="Some answer text here")
    assert rt.status == TraceStatus.SUCCESS
    assert rt.latency_ms is not None
    assert rt.latency_ms > 400
    assert rt.final_answer_preview == "Some answer text here"
    assert rt.error is None


def test_request_trace_finalize_error():
    rt = RequestTrace(trace_id="t1", started_at=time.time() - 0.3)
    rt.finalize(error="Something broke")
    assert rt.status == TraceStatus.ERROR
    assert rt.error == "Something broke"


def test_request_trace_finalize_partial():
    rt = RequestTrace(trace_id="t1", started_at=time.time() - 0.2)
    rt.add_tool_trace(ToolTrace(tool_name="vs", success=True))
    rt.add_tool_trace(ToolTrace(tool_name="kg", success=False))
    rt.finalize(answer="partial answer")
    assert rt.status == TraceStatus.PARTIAL


def test_request_trace_to_dict():
    rt = RequestTrace(trace_id="t1", started_at=time.time() - 0.1)
    rt.add_tool_trace(ToolTrace(tool_name="vs", success=True, evidence_count=3, latency_ms=50.0))
    rt.finalize(answer="Hello world")
    d = rt.to_dict()
    assert d["trace_id"] == "t1"
    assert d["status"] == "success"
    assert len(d["tool_traces"]) == 1
    assert d["tool_traces"][0]["tool_name"] == "vs"
    assert d["tool_traces"][0]["evidence_count"] == 3
