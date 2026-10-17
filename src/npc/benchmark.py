"""Compare action usefulness probabilities against human-authored binary labels."""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from npc.action_ranking import (
    PROMPT_VERSION,
    InvalidEvaluationError,
    RankedAction,
    SystemOneEvaluator,
    rank_actions,
)
from npc.system_one import SystemOneError

USEFULNESS_THRESHOLD = 0.5


@dataclass(frozen=True)
class BenchmarkCase:
    """Ranking inputs and local-only usefulness labels."""

    id: str
    intent: str
    state: str
    actions: list[str]
    relevant_actions: list[str]


@dataclass
class CaseResult:
    """Observed probabilities and their mean squared error against usefulness."""

    id: str
    ranking: list[RankedAction]
    relevant_actions: list[str]
    elapsed_seconds: float
    error: str | None
    brier_score: float | None = None
    failed_actions: list[str] | None = None


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonblank string in benchmark fixture")
    return value


def _names(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Expected a list in benchmark fixture")
    names = [_text(item).strip() for item in value]
    if len(names) != len(set(names)):
        raise ValueError("Benchmark names must be unique after trimming")
    return names


def _case(value: object) -> BenchmarkCase:
    if not isinstance(value, dict):
        raise ValueError("Expected a benchmark case object")
    case = BenchmarkCase(
        id=_text(value.get("id")),
        intent=_text(value.get("intent")),
        state=_text(value.get("state")),
        actions=_names(value.get("actions")),
        relevant_actions=_names(value.get("relevant_actions")),
    )
    if not set(case.relevant_actions) <= set(case.actions):
        raise ValueError(f"{case.id}: relevance labels must name available actions")
    return case


def load_cases(path: Path) -> list[BenchmarkCase]:
    """Load UTF-8 JSON cases, rejecting inconsistent labels and duplicate IDs."""
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Benchmark fixture must be a JSON array")
    cases = [_case(value) for value in payload]
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Benchmark case IDs must be unique")
    return cases


def _evaluate(case: BenchmarkCase, evaluator: SystemOneEvaluator) -> CaseResult:
    started = perf_counter()
    try:
        ranking = rank_actions(
            case.intent, case.state, case.actions, evaluator=evaluator
        )
    except (SystemOneError, InvalidEvaluationError) as error:
        return CaseResult(
            case.id,
            [],
            case.relevant_actions,
            perf_counter() - started,
            f"{type(error).__name__}: {error}",
        )
    result = CaseResult(
        case.id,
        ranking,
        case.relevant_actions,
        perf_counter() - started,
        None,
    )
    result.failed_actions = [
        item.action
        for item in ranking
        if (item.probability >= USEFULNESS_THRESHOLD)
        != (item.action in case.relevant_actions)
    ]
    if ranking:
        result.brier_score = sum(
            (item.probability - int(item.action in case.relevant_actions)) ** 2
            for item in ranking
        ) / len(ranking)
    return result


def run_benchmark(
    cases: list[BenchmarkCase],
    *,
    evaluator: SystemOneEvaluator,
) -> dict[str, object]:
    """Return rankings and Brier scores using the same evaluation as rank_actions.

    Useful actions have target 1; all other actions have target 0. Lower scores
    are better. Each evaluated action has equal weight in the overall mean.
    Labels stay local. Empty catalogs and failed requests contribute no scores.
    Scores at least 0.5 predict useful. A case fails if any prediction differs
    from its label. Request errors remain separate from prediction failures.
    """
    started = perf_counter()
    results = []
    model = None
    for case in cases:
        result = _evaluate(case, evaluator)
        results.append(result)
        if model is None and result.ranking:
            name = getattr(evaluator, "model", None)
            if isinstance(name, str):
                model = name
    evaluated_actions = sum(len(result.ranking) for result in results)
    squared_error = sum(
        result.brier_score * len(result.ranking)
        for result in results
        if result.brier_score is not None
    )
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "elapsed_seconds": perf_counter() - started,
        "metrics": {
            "total_cases": len(results),
            "failed_cases": sum(bool(result.failed_actions) for result in results),
            "failed_actions": sum(
                len(result.failed_actions or []) for result in results
            ),
            "usefulness_threshold": USEFULNESS_THRESHOLD,
            "request_error_cases": sum(result.error is not None for result in results),
            "evaluated_actions": evaluated_actions,
            "brier_score": squared_error / evaluated_actions
            if evaluated_actions
            else None,
        },
        "results": [asdict(result) for result in results],
    }
