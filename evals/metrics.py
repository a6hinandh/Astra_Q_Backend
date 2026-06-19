from __future__ import annotations

from typing import Any


def exact_match(a: str, b: str) -> bool:
    return a == b


def contains_all_keywords(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return all(kw.lower() in lower for kw in keywords)


def precision_recall_f1(
    predicted_items: list[Any], expected_items: list[Any]
) -> dict[str, float]:
    pred_set = set(predicted_items)
    exp_set = set(expected_items)
    true_positives = len(pred_set & exp_set)
    precision = true_positives / len(pred_set) if pred_set else 0.0
    recall = true_positives / len(exp_set) if exp_set else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def routing_accuracy(results: list[dict[str, Any]]) -> float:
    correct = sum(1 for r in results if r.get("mode_matched", False))
    return correct / len(results) if results else 0.0


def tool_selection_accuracy(results: list[dict[str, Any]]) -> float:
    correct = sum(1 for r in results if r.get("tools_matched", False))
    return correct / len(results) if results else 0.0


def mean_score(results: list[dict[str, Any]], key: str = "score") -> float:
    scores = [r.get(key, 0.0) for r in results]
    return sum(scores) / len(scores) if scores else 0.0


def reciprocal_rank(
    retrieved_sources: list[str], expected_keywords: list[str]
) -> float:
    if not expected_keywords:
        return 0.0
    for rank, source in enumerate(retrieved_sources, start=1):
        for kw in expected_keywords:
            if kw.lower() in source.lower():
                return 1.0 / rank
    return 0.0


def mrr(scores: list[float]) -> float:
    return sum(scores) / len(scores) if scores else 0.0
