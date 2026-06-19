"""Tests for core/config.py — must pass without any external services."""

import os
from core.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.GOOGLE_API_KEY == ""
    assert s.GEMINI_API_KEY == ""
    assert s.effective_gemini_key == ""
    assert s.NEO4J_URI == "bolt://localhost:7687"
    assert s.NEO4J_USERNAME == "neo4j"
    assert s.NEO4J_DATABASE == "neo4j"
    assert s.FIREBASE_SERVICE_ACCOUNT_JSON == ""
    assert s.GOOGLE_APPLICATION_CREDENTIALS == ""


def test_cors_parsing_default():
    s = Settings()
    origins = s.cors_allowed_origins
    assert "http://localhost:5173" in origins
    assert "http://localhost:5174" in origins


def test_cors_parsing_custom(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://example.com")
    s = Settings()
    origins = s.cors_allowed_origins
    assert len(origins) == 2
    assert "http://localhost:3000" in origins
    assert "http://example.com" in origins


def test_cors_parsing_empty(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "")
    s = Settings()
    assert s.cors_allowed_origins == ["http://localhost:5173"]


def test_effective_gemini_key_prefers_google_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key-123")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key-456")
    s = Settings()
    assert s.effective_gemini_key == "google-key-123"


def test_effective_gemini_key_falls_back(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key-456")
    s = Settings()
    assert s.effective_gemini_key == "gemini-key-456"
