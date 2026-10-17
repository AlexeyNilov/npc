"""Measure action usefulness probabilities against binary labels with Brier scores."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx2

from npc.benchmark import load_cases, run_benchmark
from npc.system_one import SystemOneClient, validate_endpoint


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Requires SYSTEM_ONE containing the complete endpoint URL. Example: "
            "npc-benchmark --input tests/fixtures/action_ranking/cases.json "
            "--output /tmp/action-ranking-report.json. "
            "Exit codes: 0 completed, 1 configuration/I/O error, "
            "2 report saved with case errors. Brier scores measure probability error "
            "and do not change the exit code."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="UTF-8 JSON cases with id, intent, state, actions, and relevant_actions",
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
        cases = load_cases(args.input)
        with httpx2.Client() as client:
            evaluator = SystemOneClient(endpoint, client=client, timeout=args.timeout)
            report = run_benchmark(cases, evaluator=evaluator)
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
            args.output.write_text(text, encoding="utf-8")
    except (ValueError, OSError) as error:
        print(f"Benchmark failed: {error}", file=sys.stderr)
        return 1
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    return 2 if metrics["error_cases"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
