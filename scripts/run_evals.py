from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path when running from scripts/
_HERE = Path(__file__).resolve().parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from evals.agent_eval import run_agent_eval
from evals.report import generate_markdown_report
from evals.routing_eval import run_routing_eval

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

ROUTING_THRESHOLD = 0.70
AGENT_THRESHOLD = 0.70
REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "evaluation_report.md"


def main() -> int:
    logger.info("Running routing benchmark...")
    routing_result = run_routing_eval()

    logger.info("Running agent workflow benchmark...")
    agent_result = run_agent_eval()

    results = [routing_result, agent_result]
    report_path = generate_markdown_report(results, REPORT_PATH)

    print()
    print("=" * 60)
    print("  Vanta AI — Evaluation Summary")
    print("=" * 60)
    for r in results:
        pct = round(r.score * 100, 1)
        print(f"  {r.suite_name:40s} {r.passed:3d}/{r.total:<3d}  {pct:5.1f}%")
    print("=" * 60)

    routing_ok = routing_result.score >= ROUTING_THRESHOLD
    agent_ok = agent_result.score >= AGENT_THRESHOLD

    if not routing_ok:
        logger.warning(
            "Routing benchmark below threshold "
            "(%.1f%% < %.0f%% threshold)",
            routing_result.score * 100,
            ROUTING_THRESHOLD * 100,
        )
    if not agent_ok:
        logger.warning(
            "Agent benchmark below threshold "
            "(%.1f%% < %.0f%% threshold)",
            agent_result.score * 100,
            AGENT_THRESHOLD * 100,
        )

    print(f"\n  Report saved to: {report_path}")
    print()

    if routing_ok and agent_ok:
        logger.info("All benchmarks passed thresholds.")
        return 0
    else:
        logger.warning("Some benchmarks below threshold.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
