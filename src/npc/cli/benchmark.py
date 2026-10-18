"""Benchmark action usefulness or whole-plan suitability."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx2

from npc.benchmarks import action_ranking, plan_ranking
from npc.system_one import SystemOneClient, validate_endpoint

BENCHMARKS = {
    "action-ranking": action_ranking.run,
    "plan-ranking": plan_ranking.run,
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Requires SYSTEM_ONE containing the complete endpoint URL. Example: "
            "npc-benchmark --input benchmarks/action_ranking.json "
            "--output /tmp/action-ranking-report.json. "
            "Exit codes: 0 completed, 1 configuration/I/O error, "
            "2 report saved with request errors. Scores >= 0.5 predict useful or suitable; "
            "failed_cases counts cases with any mislabeled prediction. "
            "Brier scores weight each candidate equally; lower is better. "
            "Empty catalogs and request errors contribute no score. "
            "Prediction failures and Brier scores do not change the exit code. "
            "Plan example: npc-benchmark --benchmark plan-ranking "
            "--input benchmarks/plan_ranking.json --output runs/plans.json. "
            "Add cases by copying the selected dataset format. "
            "Each report includes inputs, labels, predictions, and a dataset SHA-256 hash."
        ),
    )
    parser.add_argument(
        "--benchmark",
        choices=BENCHMARKS,
        default="action-ranking",
        help="Benchmark to run (default: action-ranking)",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help=(
            "UTF-8 JSON array of cases with id and state; action-ranking uses "
            "actions and relevant_actions, plan-ranking uses plans and acceptable_plans. "
            "state contains nonblank intent and situation plus optional string fields. "
            "IDs must be unique. Candidate and label lists contain unique nonblank "
            "strings, trimmed before evaluation; labels must name candidates. "
            "At most 10 candidates per case. State omits available_actions for "
            "actions or available_plans for plans; the ranker supplies that field"
        ),
    )
    parser.add_argument(
        "--output", type=Path, help="Write JSON report to this file (default: stdout)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Positive finite HTTP timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--model-version", help="Exact model revision/hash for comparisons"
    )
    parser.add_argument(
        "--server-version", help="Server revision/build for comparisons"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Load endpoint configuration, evaluate cases, and write a JSON report."""
    args = _parser().parse_args(argv)
    try:
        endpoint = validate_endpoint(os.environ.get("SYSTEM_ONE", ""))
        with httpx2.Client() as client:
            evaluator = SystemOneClient(endpoint, client=client, timeout=args.timeout)
            report = BENCHMARKS[args.benchmark](args.input, evaluator=evaluator)
        report.update(
            endpoint=endpoint,
            model_version=args.model_version,
            server_version=args.server_version,
            timeout_seconds=args.timeout,
        )
        text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output is None:
            sys.stdout.write(text)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
    except (ValueError, OSError) as error:
        print(f"Benchmark failed: {error}", file=sys.stderr)
        return 1
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    return 2 if metrics["request_error_cases"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
