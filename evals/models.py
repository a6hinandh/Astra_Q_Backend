from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RoutingExample:
    id: str
    query: str
    expected_mode: str
    expected_tools: list[str]
    notes: str = ""


@dataclass
class AgentEvalExample:
    id: str
    query: str
    expected_mode: str
    expected_tools: list[str]
    expected_source_keywords: list[str] = field(default_factory=list)
    expected_answer_keywords: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class EvalResult:
    id: str
    passed: bool
    score: float
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalSuiteResult:
    suite_name: str
    total: int
    passed: int
    failed: int
    score: float
    results: list[EvalResult] = field(default_factory=list)
