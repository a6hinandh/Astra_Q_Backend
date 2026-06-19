"""Tests for tools/registry.py — must pass without external services."""

import pytest
from tools.registry import (
    ToolRegistry,
    DuplicateToolError,
    ToolNotFoundError,
)
from tools.base import BaseTool
from core.models import ToolInput, ToolResult


class _DummyTool(BaseTool):
    name = "dummy"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {"query": {"type": "string"}}}

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.ok(
            self.name,
            evidence=[],
            answer="dummy response",
        )


class _AnotherTool(BaseTool):
    name = "another"
    description = "Another dummy tool"
    input_schema = None

    def run(self, input: ToolInput) -> ToolResult:
        return ToolResult.ok(self.name, evidence=[])


def test_registry_register_and_list():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    registry.register(_AnotherTool())

    tools = registry.list_tools()
    names = [t["name"] for t in tools]
    assert "dummy" in names
    assert "another" in names
    assert len(tools) == 2


def test_registry_get():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    tool = registry.get("dummy")
    assert isinstance(tool, _DummyTool)


def test_registry_duplicate_name_raises():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    with pytest.raises(DuplicateToolError, match="already registered"):
        registry.register(_DummyTool())


def test_registry_missing_tool_raises():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError, match="not found"):
        registry.get("nonexistent")


def test_registry_run_tool():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    result = registry.run_tool("dummy", "test query")
    assert result.success is True
    assert result.tool_name == "dummy"


def test_registry_run_tool_with_kwargs():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    result = registry.run_tool("dummy", "test query", extra="value")
    assert result.success is True
    assert result.tool_name == "dummy"


def test_registry_list_metadata_structure():
    registry = ToolRegistry()
    registry.register(_DummyTool())
    entries = registry.list_tools()
    for entry in entries:
        assert "name" in entry
        assert "description" in entry
        assert "input_schema" in entry


def test_empty_registry_list():
    registry = ToolRegistry()
    assert registry.list_tools() == []
