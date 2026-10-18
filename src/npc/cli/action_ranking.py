"""Rank available actions by independent relevance or comparative choice."""

import argparse
import json
import math
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import httpx2

from npc.action_ranking import (
    MAX_ACTIONS,
    RankedAction,
    rank_actions_by_choice,
    rank_actions_by_relevance,
    validate_ranking_inputs,
)
from npc.model.evaluation import State
from npc.system_one import (
    InvalidEvaluationError,
    SystemOneClient,
    SystemOneError,
    validate_endpoint,
)

type Approach = Literal["relevance", "choice"]


def _timeout(text: str) -> float:
    try:
        value = float(text)
        if math.isfinite(value) and value > 0:
            return value
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("timeout must be positive and finite")


def _parser(approach: Approach) -> argparse.ArgumentParser:
    command = f"npc-rank-actions-by-{approach}"
    meaning = (
        "Scores sum to one and express relative preference among these actions. "
        if approach == "choice"
        else "Scores express independent usefulness and need not sum to one. "
    )
    parser = argparse.ArgumentParser(
        prog=command,
        description=f"Rank available actions by {approach} as the next step toward an intent.",
        epilog=(
            'Input: one JSON object with "state": an object of string fields '
            'including nonblank "intent" and "situation", and "actions": '
            "an array of unique nonblank strings. "
            f"At most {MAX_ACTIONS} actions are accepted. "
            "Action names are trimmed and must be unique after trimming. "
            "Additional state fields are preserved. State must omit available_actions; "
            "the ranker supplies it. Unknown outer fields are rejected. "
            "Output: a JSON array of action/score objects, "
            "sorted by descending probability, preserving ties and raw scores. "
            f"{meaning}Requires SYSTEM_ONE containing the complete "
            "endpoint URL for nonempty actions. Empty actions return []. "
            f"Examples: {command} --input request.json; "
            f"cat request.json | {command}. "
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


def _request(text: str) -> tuple[State, list[str]]:
    payload = json.loads(text)
    if not isinstance(payload, dict) or payload.keys() != {
        "state",
        "actions",
    }:
        raise ValueError("Expected an object containing only state and actions")
    state, actions = payload["state"], payload["actions"]
    if not isinstance(actions, list):
        raise ValueError("actions must be an array")
    return state, validate_ranking_inputs(state, actions)


def _rank(
    state: State, actions: list[str], timeout: float, approach: Approach
) -> list[RankedAction]:
    # Validate the JSON before this shortcut so empty catalogs still require context.
    if not actions:
        return []
    endpoint = validate_endpoint(os.environ.get("SYSTEM_ONE", ""))
    with httpx2.Client() as client:
        evaluator = SystemOneClient(endpoint, client=client, timeout=timeout)
        rank = (
            rank_actions_by_choice
            if approach == "choice"
            else rank_actions_by_relevance
        )
        return rank(state, actions, evaluator=evaluator)


def _main(argv: Sequence[str] | None, approach: Approach) -> int:
    """Read one request and write a complete ranking or a categorized error."""
    args = _parser(approach).parse_args(argv)
    try:
        text = (
            sys.stdin.read()
            if args.input == "-"
            else Path(args.input).read_text(encoding="utf-8")
        )
        try:
            state, actions = _request(text)
        except ValueError as error:
            print(f"Invalid input: {error}", file=sys.stderr)
            return 2
        try:
            ranking = _rank(state, actions, args.timeout, approach)
        except InvalidEvaluationError as error:
            print(f"Invalid response: {error}", file=sys.stderr)
            return 1
        except SystemOneError as error:
            print(f"Dependency error: {error}", file=sys.stderr)
            return 1
        except ValueError as error:
            print(f"Configuration error: {error}", file=sys.stderr)
            return 1
        output = [
            {"action": item.action, "score": item.probability} for item in ranking
        ]
        sys.stdout.write(json.dumps(output, ensure_ascii=False, allow_nan=False) + "\n")
    except (OSError, UnicodeError) as error:
        print(f"I/O error: {error}", file=sys.stderr)
        return 1
    return 0


def main_by_relevance(argv: Sequence[str] | None = None) -> int:
    """Rank actions by independent usefulness."""
    return _main(argv, "relevance")


def main_by_choice(argv: Sequence[str] | None = None) -> int:
    """Rank actions by relative preference among candidates."""
    return _main(argv, "choice")


if __name__ == "__main__":
    raise SystemExit(main_by_relevance())
