# Vanta AI Evaluation Report

**Generated:** 2026-06-19 14:18 UTC

## Suite Summary

| Suite | Total | Passed | Failed | Score |
|-------|-------|--------|--------|-------|
| Routing & Planner Benchmark | 22 | 22 | 0 | 100.0% |
| Agent Workflow Benchmark | 10 | 10 | 0 | 100.0% |

**Overall:** 32/32 passed, average score **100.0%**

## Known Limitations

- Benchmarks are lightweight and run locally without external services.
- Routing accuracy reflects the current heuristic-based router (`backend/api/router_logic.py`).
- Tool selection accuracy tests the Planner's `decompose()` method, which currently returns a fixed plan.
- Agent workflow benchmarks use fake tools that return controlled synthetic data.
- No live retrieval quality benchmark (MRR over real indexed documents) yet.
- No full hallucination or grounding evaluator yet.
- Trace quality checks are not yet benchmarked.

## Future Work

- Retrieval MRR evaluation over real FAISS index
- Grounded answer evaluation with citation overlap scoring
- Trace quality benchmarks (latency, completeness)
- Multi-turn conversation evaluation
- Integration with CI pipeline
