from __future__ import annotations

from typing import Any


def answer_has_source_overlap(
    answer: str, sources: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Basic heuristic: check how many source content keywords appear in the answer.

    This is a lightweight grounding indicator, NOT a full hallucination detector.
    """
    if not sources:
        return {"overlap_ratio": 0.0, "matched_keywords": []}

    answer_lower = answer.lower()
    all_keywords: set[str] = set()
    for src in sources:
        content = src.get("content", "") or src.get("source", "")
        for word in content.lower().split():
            if len(word) > 3:
                all_keywords.add(word)

    if not all_keywords:
        return {"overlap_ratio": 0.0, "matched_keywords": []}

    matched = [kw for kw in all_keywords if kw in answer_lower]
    overlap_ratio = len(matched) / len(all_keywords)
    return {
        "overlap_ratio": round(overlap_ratio, 4),
        "matched_keywords": matched[:50],
        "total_keywords": len(all_keywords),
    }
