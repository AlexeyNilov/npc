"""Compare noul and choice ranking on the maintained action benchmark."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx2

from npc.benchmarks.action_comparison import run_comparison
from npc.benchmarks.action_ranking import load_cases
from npc.system_one import SystemOneClient, validate_endpoint


def main(argv: Sequence[str] | None = None) -> int:
    """Run both production rankers and save native and comparable metrics."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Requires SYSTEM_ONE containing the full endpoint URL. Runs noul then choice. "
            "Input is the existing action-ranking JSON dataset with id, state, actions, "
            "and relevant_actions. Labels remain local. Top1 accuracy and mean reciprocal "
            "rank use paired successful cases with at least one relevant action. Ties "
            "retain input order. No-relevant and empty catalogs are counted separately. "
            "Noul keeps its native threshold and Brier metrics; choice has no binary "
            "calibration metrics. Reports include raw rankings, errors, timing, models, "
            "prompt versions, and a hash of normalized dataset inputs. "
            "Example: python -m experiments.action_ranking_comparison. "
            "Exit codes: 0 completed, 1 configuration/input/I/O error, 2 saved with request errors."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("benchmarks/action_ranking.json"),
        help="Action dataset (default: benchmarks/action_ranking.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runs/action-ranking-comparison.json"),
        help="JSON report (default: runs/action-ranking-comparison.json)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Positive finite HTTP timeout in seconds (default: 30)",
    )
    args = parser.parse_args(argv)
    try:
        cases = load_cases(args.input)
        endpoint = validate_endpoint(os.environ.get("SYSTEM_ONE", ""))
        with httpx2.Client() as client:
            evaluator = SystemOneClient(endpoint, client=client, timeout=args.timeout)
            report = run_comparison(
                cases,
                evaluator=evaluator,
                choice_evaluator=evaluator,
            )
        report.update(endpoint=endpoint, timeout_seconds=args.timeout)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    except (ValueError, OSError) as error:
        print(f"Comparison failed: {error}", file=sys.stderr)
        return 1
    for name in ("noul", "choice"):
        approach = report[name]
        assert isinstance(approach, dict)
        if approach["metrics"]["request_error_cases"]:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
