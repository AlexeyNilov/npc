"""Execute cases and score binary labels without owning ranking prompts."""

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from time import perf_counter

from npc.model.evaluation import Evaluator, State
from npc.system_one import InvalidEvaluationError, SystemOneError

USEFULNESS_THRESHOLD = 0.5


@dataclass(frozen=True)
class Case:
    """Inputs and binary labels shared by ranking benchmarks."""

    id: str
    state: State
    candidates: list[str]
    labels: list[str]


@dataclass
class Result:
    """One observation; errors and empty catalogs contribute no Brier score."""

    case: Case
    ranking: list[tuple[str, float]]
    elapsed_seconds: float
    error: str | None = None
    brier_score: float | None = None
    failed: list[str] | None = None


def _evaluate(case: Case, predict: Callable[[Case], list[tuple[str, float]]]) -> Result:
    started = perf_counter()
    try:
        ranking = predict(case)
    except (SystemOneError, InvalidEvaluationError) as error:
        return Result(
            case, [], perf_counter() - started, f"{type(error).__name__}: {error}"
        )
    return Result(case, ranking, perf_counter() - started)


def _score(result: Result) -> None:
    if result.error is not None:
        return
    result.failed = [
        name
        for name, probability in result.ranking
        if (probability >= USEFULNESS_THRESHOLD) != (name in result.case.labels)
    ]
    if result.ranking:
        result.brier_score = sum(
            (probability - int(name in result.case.labels)) ** 2
            for name, probability in result.ranking
        ) / len(result.ranking)


def _metrics(results: list[Result], plural: str) -> dict[str, object]:
    count = sum(len(result.ranking) for result in results)
    squared_error = sum(
        result.brier_score * len(result.ranking)
        for result in results
        if result.brier_score is not None
    )
    return {
        "total_cases": len(results),
        "failed_cases": sum(bool(result.failed) for result in results),
        f"failed_{plural}": sum(len(result.failed or []) for result in results),
        "usefulness_threshold": USEFULNESS_THRESHOLD,
        "request_error_cases": sum(result.error is not None for result in results),
        f"evaluated_{plural}": count,
        "brier_score": squared_error / count if count else None,
    }


def _serialize(
    result: Result, candidate_name: str, label_name: str
) -> dict[str, object]:
    return {
        "id": result.case.id,
        "state": result.case.state,
        f"{candidate_name}s": result.case.candidates,
        label_name: result.case.labels,
        "ranking": [
            {candidate_name: name, "probability": probability}
            for name, probability in result.ranking
        ],
        "elapsed_seconds": result.elapsed_seconds,
        "error": result.error,
        "brier_score": result.brier_score,
        f"failed_{candidate_name}s": result.failed,
    }


def run_cases(
    cases: list[Case],
    *,
    predict: Callable[[Case], list[tuple[str, float]]],
    evaluator: Evaluator,
    benchmark: str,
    prompt_version: str,
    candidate_name: str,
    label_name: str,
) -> dict[str, object]:
    """Run sequentially, preserving failures and weighting each prediction equally.

    The callback calls the production ranker with the injected evaluator. Labels
    remain local. Brier scores use targets 1 for labeled candidates and 0 for
    others. Scores at least 0.5 predict useful or suitable. A case fails when any
    prediction disagrees with its label. Programming errors propagate.
    """
    results, model, elapsed = observe_cases(cases, predict=predict, evaluator=evaluator)
    for result in results:
        _score(result)
    inputs = json.dumps(
        [asdict(case) for case in cases], sort_keys=True, ensure_ascii=False
    )
    return {
        "benchmark": benchmark,
        "dataset_hash": sha256(inputs.encode("utf-8")).hexdigest(),
        "created_at": datetime.now(UTC).isoformat(),
        "prompt_version": prompt_version,
        "model": model,
        "elapsed_seconds": elapsed,
        "metrics": _metrics(results, f"{candidate_name}s"),
        "results": [
            _serialize(result, candidate_name, label_name) for result in results
        ],
    }


def observe_cases(
    cases: list[Case],
    *,
    predict: Callable[[Case], list[tuple[str, float]]],
    evaluator: object,
) -> tuple[list[Result], str | None, float]:
    """Collect raw observations for experiments without judging their correctness.

    Returns results, the first observed model name, and total elapsed seconds.
    Request and response errors remain attached to their cases; later cases run.
    """
    started = perf_counter()
    results = []
    model = None
    for case in cases:
        result = _evaluate(case, predict)
        results.append(result)
        if model is None and result.ranking:
            name = getattr(evaluator, "model", None)
            if isinstance(name, str):
                model = name
    return results, model, perf_counter() - started
