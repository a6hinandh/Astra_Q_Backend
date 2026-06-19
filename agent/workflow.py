from __future__ import annotations

import logging
from typing import Any

from agent.executor import AgentExecutor
from agent.planner import AgentPlanner
from agent.synthesizer import AgentSynthesizer
from core.tracing import agent_trace_context
from tools import get_default_registry
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def run_agent_query(query: str, registry: ToolRegistry | None = None) -> str:
    if registry is None:
        registry = get_default_registry()
    planner = AgentPlanner()
    executor = AgentExecutor(registry)
    synthesizer = AgentSynthesizer()
    with agent_trace_context("workflow") as _trace:
        plan = planner.decompose(query)
        results = executor.execute(plan)
        answer = synthesizer.synthesize(query, results)
    return answer
