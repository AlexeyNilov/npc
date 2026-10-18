"""Observe score changes after changing one context fact, without correctness labels."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx2

from npc.benchmarks.runner import Case, observe_cases
from npc.plan_ranking import PROMPT_VERSION, rank_plans
from npc.system_one import SystemOneClient, validate_endpoint


def build_cases() -> list[Case]:
    """Preserve the original four scenarios and candidate plans."""
    situation = (
        "Checkout started failing after the latest release. Logs are available but unread. "
        "The previous release is compatible with the current database schema, and rollback is available. "
        "No recovery work has been completed."
    )
    plans = [
        "Inspect application logs and compare errors with the release changes. Roll back if the release caused the failure, then verify checkout and monitor error rates.",
        "Roll back to the previous release immediately. Verify checkout and monitor error rates, then inspect logs to identify the cause.",
        "Delete the production database and redeploy the latest release. Check whether checkout works afterward.",
        "Update the dashboard colors and wait until tomorrow before investigating checkout failures.",
    ]
    changes = {
        "baseline": situation,
        "incompatible_database": situation.replace("is compatible", "is incompatible"),
        "failures_predate_release": situation.replace(
            "after the latest", "before the latest"
        ),
        "known_unrelated_cause": situation.replace(
            "Logs are available but unread.",
            "Logs have been read and identify an expired payment-provider credential as the cause, unrelated to the release.",
        ),
    }
    return [
        Case(
            name,
            {
                "intent": "Restore checkout service while preserving customer data.",
                "situation": text,
            },
            plans.copy(),
            [],
        )
        for name, text in changes.items()
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Save raw rankings and score deltas using the shared observation runner."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Requires SYSTEM_ONE. Exit codes: 0 completed, 1 configuration/I/O error, 2 saved with request errors. Deltas are observations, not correctness judgments.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runs/plan-context-sensitivity.json"),
        help="JSON report path (default: runs/plan-context-sensitivity.json)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Positive finite HTTP timeout in seconds (default: 30)",
    )
    args = parser.parse_args(argv)
    try:
        endpoint = validate_endpoint(os.environ.get("SYSTEM_ONE", ""))
        with httpx2.Client() as client:
            evaluator = SystemOneClient(endpoint, client=client, timeout=args.timeout)
            results, model, elapsed = observe_cases(
                build_cases(),
                predict=lambda case: [
                    (item.plan, item.probability)
                    for item in rank_plans(
                        case.state, case.candidates, evaluator=evaluator
                    )
                ],
                evaluator=evaluator,
            )
        baseline = dict(results[0].ranking)
        report = {
            "model": model,
            "prompt_version": PROMPT_VERSION,
            "endpoint": endpoint,
            "elapsed_seconds": elapsed,
            "results": [
                {
                    "id": result.case.id,
                    "state": result.case.state,
                    "plans": result.case.candidates,
                    "elapsed_seconds": result.elapsed_seconds,
                    "error": result.error,
                    "ranking": [
                        {
                            "plan": plan,
                            "probability": score,
                            "delta_from_baseline": score - baseline[plan]
                            if plan in baseline
                            else None,
                        }
                        for plan, score in result.ranking
                    ],
                }
                for result in results
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    except (ValueError, OSError) as error:
        print(f"Experiment failed: {error}", file=sys.stderr)
        return 1
    return 2 if any(result.error is not None for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
