"""Rank supplied short-text plans by whole-plan suitability."""

import argparse
import json
import math
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx2

from npc.plan_ranking import (
    MAX_PLANS,
    RankedPlan,
    rank_plans,
    validate_ranking_inputs,
)
from npc.system_one import (
    InvalidEvaluationError,
    SystemOneClient,
    SystemOneError,
    validate_endpoint,
)


def _timeout(text: str) -> float:
    try:
        value = float(text)
        if math.isfinite(value) and value > 0:
            return value
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("timeout must be positive and finite")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            'Input: one JSON object with required nonblank string fields "intent" '
            'and "state", and "plans": an array of unique nonblank strings. '
            f"At most {MAX_PLANS} plans are accepted. "
            "Plan texts are trimmed and must be unique after trimming. "
            "Unknown fields are rejected. Output: a JSON array of plan/score objects, "
            "sorted by descending suitability probability, preserving ties and raw scores. "
            "Scores need not sum to one. Requires SYSTEM_ONE containing the complete "
            "endpoint URL for nonempty plans. Empty plans return []. "
            "Examples: npc-rank-plans --input request.json; "
            "cat request.json | npc-rank-plans. "
            "Exit codes: 0 success, 1 configuration/I/O/dependency/response error, "
            "2 invalid arguments or input. Errors go to stderr."
        ),
    )
    parser.add_argument(
        "--input", default="-", help="UTF-8 JSON file (default: -, meaning stdin)"
    )
    parser.add_argument(
        "--timeout",
        type=_timeout,
        default=30.0,
        help="Positive finite HTTP timeout in seconds (default: 30)",
    )
    return parser


def _request(text: str) -> tuple[str, str, list[str]]:
    payload = json.loads(text)
    if not isinstance(payload, dict) or payload.keys() != {
        "intent",
        "state",
        "plans",
    }:
        raise ValueError("Expected an object containing only intent, state, and plans")
    intent, state, plans = payload["intent"], payload["state"], payload["plans"]
    if not isinstance(plans, list):
        raise ValueError("plans must be an array")
    return intent, state, validate_ranking_inputs(intent, state, plans)


def _rank(
    intent: str, state: str, plans: list[str], timeout: float
) -> list[RankedPlan]:
    # Validate the JSON before this shortcut so empty catalogs still require context.
    if not plans:
        return []
    endpoint = validate_endpoint(os.environ.get("SYSTEM_ONE", ""))
    with httpx2.Client() as client:
        evaluator = SystemOneClient(endpoint, client=client, timeout=timeout)
        return rank_plans(intent, state, plans, evaluator=evaluator)


def main(argv: Sequence[str] | None = None) -> int:
    """Read one request and write a complete ranking or a categorized error."""
    args = _parser().parse_args(argv)
    try:
        text = (
            sys.stdin.read()
            if args.input == "-"
            else Path(args.input).read_text(encoding="utf-8")
        )
        try:
            intent, state, plans = _request(text)
        except ValueError as error:
            print(f"Invalid input: {error}", file=sys.stderr)
            return 2
        try:
            ranking = _rank(intent, state, plans, args.timeout)
        except InvalidEvaluationError as error:
            print(f"Invalid response: {error}", file=sys.stderr)
            return 1
        except SystemOneError as error:
            print(f"Dependency error: {error}", file=sys.stderr)
            return 1
        except ValueError as error:
            print(f"Configuration error: {error}", file=sys.stderr)
            return 1
        output = [{"plan": item.plan, "score": item.probability} for item in ranking]
        sys.stdout.write(json.dumps(output, ensure_ascii=False, allow_nan=False) + "\n")
    except (OSError, UnicodeError) as error:
        print(f"I/O error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
