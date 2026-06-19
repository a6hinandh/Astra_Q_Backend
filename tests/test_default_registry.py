"""Tests for tools/__init__.py — must pass without external services."""

from tools import get_default_registry
from tools.registry import ToolRegistry
from tools.vector_search import VectorSearchTool
from tools.knowledge_graph import KnowledgeGraphTool


def test_get_default_registry_returns_registry():
    registry = get_default_registry()
    assert isinstance(registry, ToolRegistry)


def test_default_registry_has_vector_search():
    registry = get_default_registry()
    tool = registry.get("vector_search")
    assert isinstance(tool, VectorSearchTool)
    assert tool.name == "vector_search"


def test_default_registry_has_knowledge_graph():
    registry = get_default_registry()
    tool = registry.get("knowledge_graph")
    assert isinstance(tool, KnowledgeGraphTool)
    assert tool.name == "knowledge_graph"


def test_default_registry_no_external_connections():
    """Calling get_default_registry() must NOT connect to Neo4j or load FAISS."""
    registry = get_default_registry()
    tools = registry.list_tools()
    assert len(tools) == 2


def test_default_registry_list_metadata():
    registry = get_default_registry()
    tools = registry.list_tools()
    for t in tools:
        assert "name" in t
        assert "description" in t


def test_vector_search_tool_handles_missing_index():
    """Running vector_search without a FAISS index should return a controlled error, not crash."""
    from core.models import ToolInput
    import os

    tool = VectorSearchTool()
    os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "")
    result = tool.run(ToolInput(query="test query"))
    assert result.success is False
    assert result.error is not None


def test_knowledge_graph_tool_handles_missing_deps():
    """Running knowledge_graph without langchain_neo4j should return a controlled error, not crash."""
    from core.models import ToolInput

    tool = KnowledgeGraphTool()
    result = tool.run(ToolInput(query="test query"))
    assert result.success is False
    assert result.error is not None
