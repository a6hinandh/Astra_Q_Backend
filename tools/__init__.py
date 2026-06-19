from tools.registry import ToolRegistry
from tools.vector_search import VectorSearchTool
from tools.knowledge_graph import KnowledgeGraphTool


def get_default_registry() -> ToolRegistry:
    """Create a ToolRegistry with the standard tools registered.

    Calling this function does NOT connect to Neo4j, load FAISS,
    call Gemini, or require Firebase. It only instantiates tool objects.
    """
    registry = ToolRegistry()
    registry.register(VectorSearchTool())
    registry.register(KnowledgeGraphTool())
    return registry


__all__ = ["get_default_registry", "ToolRegistry"]
