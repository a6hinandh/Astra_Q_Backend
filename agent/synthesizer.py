from __future__ import annotations

import logging
from typing import Any

from core.tracing import traced

logger = logging.getLogger(__name__)


class AgentSynthesizer:
    @traced(agent="synthesizer")
    def synthesize(self, query: str, results: list[dict[str, Any]]) -> str:
        logger.info("Synthesizing %d results for query: %s", len(results), query[:80])
        successful = [r for r in results if r.get("success")]
        if not successful:
            return "I could not find relevant information to answer your query."
        parts = []
        for r in successful:
            evidence = r.get("evidence")
            if evidence:
                parts.append(str(evidence))
        if not parts:
            return "No relevant information found."
        combined = "\n\n".join(parts)
        return f"Based on the available information:\n\n{combined}"
