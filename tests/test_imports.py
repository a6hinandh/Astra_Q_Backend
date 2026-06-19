"""Tests for import safety — backend.main must import without external services."""


def test_backend_imports_without_crash():
    """Importing backend.main should not require Firebase, Neo4j, or FAISS."""
    import importlib
    import sys

    # Remove any cached modules from previous runs
    for mod in list(sys.modules.keys()):
        if "backend" in mod or "core" in mod or "rag_pipeline" in mod or "kg_pipeline" in mod:
            del sys.modules[mod]

    # This import should succeed without any external services
    from backend.main import app
    assert app is not None
    assert app.title == "FastAPI"


def test_config_imports_without_crash():
    from core.config import Settings, settings
    assert isinstance(settings, Settings)
