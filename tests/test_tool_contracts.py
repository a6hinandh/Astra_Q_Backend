"""Tests for tool interface contracts — must pass without external services."""

from core.models import Evidence, ToolResult, ToolInput, ToolCall, ToolError


def test_evidence_defaults():
    ev = Evidence(content="test content", source="test_source")
    assert ev.content == "test content"
    assert ev.source == "test_source"
    assert ev.metadata == {}
    assert ev.score is None


def test_evidence_with_all_fields():
    ev = Evidence(
        content="content",
        source="src",
        metadata={"key": "val"},
        score=0.95,
    )
    assert ev.score == 0.95
    assert ev.metadata["key"] == "val"


def test_tool_result_ok():
    ev = [Evidence(content="a", source="s")]
    result = ToolResult.ok("my_tool", evidence=ev, answer="hello")
    assert result.tool_name == "my_tool"
    assert result.success is True
    assert result.metadata.get("answer") == "hello"
    assert result.error is None
    assert result.latency_ms is None


def test_tool_result_from_error():
    result = ToolResult.from_error("my_tool", "something went wrong")
    assert result.tool_name == "my_tool"
    assert result.success is False
    assert result.error == "something went wrong"


def test_tool_result_defaults():
    result = ToolResult(tool_name="t", success=True)
    assert result.evidence == []
    assert result.error is None
    assert result.metadata == {}
    assert result.latency_ms is None


def test_tool_input_defaults():
    inp = ToolInput(query="hello")
    assert inp.query == "hello"
    assert inp.parameters == {}


def test_tool_input_with_params():
    inp = ToolInput(query="q", parameters={"history": []})
    assert inp.parameters["history"] == []


def test_tool_call_defaults():
    tc = ToolCall(tool_name="t", input=ToolInput(query="q"))
    assert tc.call_id == ""


def test_tool_error_is_exception():
    assert issubclass(ToolError, Exception)


def test_tool_result_latency():
    result = ToolResult(tool_name="t", success=True, latency_ms=42.5)
    assert result.latency_ms == 42.5
