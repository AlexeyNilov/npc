"""Load labeled scenarios and compare action probabilities against their tiers."""

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


@dataclass(frozen=True)
class BenchmarkCase:
    """Inputs and local-only labels for one ranking scenario."""

    id: str
    pair_id: str | None
    intent: str
    state: str
    actions: list[str]
    expected_tiers: list[list[str]]
    relevant_actions: list[str]


@dataclass
class CaseResult:
    """Observed ranking and comparisons; errors contain no fabricated scores."""

    id: str
    pair_id: str | None
    ranking: list[RankedAction]
    model: str | None
    elapsed_seconds: float
    error: str | None
    pairwise_ordering_accuracy: float | None = None
    top_action_relevant: bool | None = None
    max_probability: float | None = None


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonblank string in benchmark fixture")
    return value


def _names(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Expected a list in benchmark fixture")
    names = [_text(item) for item in value]
    if len(names) != len(set(names)):
        raise ValueError("Benchmark names must be unique")
    return names


def _case(value: object) -> BenchmarkCase:
    if not isinstance(value, dict):
        raise ValueError("Expected a benchmark case object")
    tiers = value.get("expected_tiers")
    if not isinstance(tiers, list):
        raise ValueError("Expected a list of ranking tiers")
    case = BenchmarkCase(
        id=_text(value.get("id")),
        pair_id=None if value.get("pair_id") is None else _text(value["pair_id"]),
        intent=_text(value.get("intent")),
        state=_text(value.get("state")),
        actions=_names(value.get("actions")),
        expected_tiers=[_names(tier) for tier in tiers],
        relevant_actions=_names(value.get("relevant_actions")),
    )
    _validate_labels(case)
    return case


def _validate_labels(case: BenchmarkCase) -> None:
    flattened = [name for tier in case.expected_tiers for name in tier]
    if (
        len(flattened) != len(case.actions)
        or set(flattened) != set(case.actions)
        or not all(case.expected_tiers)
    ):
        raise ValueError(f"{case.id}: tiers must contain every action exactly once")
    if not set(case.relevant_actions) <= set(case.actions):
        raise ValueError(f"{case.id}: relevance labels must name available actions")


def load_cases(path: Path) -> list[BenchmarkCase]:
    """Load UTF-8 JSON cases, rejecting inconsistent labels and duplicate IDs."""
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Benchmark fixture must be a JSON array")
    cases = [_case(value) for value in payload]
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Benchmark case IDs must be unique")
    _validate_pairs(cases)
    return cases


def _validate_pairs(cases: list[BenchmarkCase]) -> None:
    pairs: dict[str, list[BenchmarkCase]] = {}
    for case in cases:
        if case.pair_id is not None:
            pairs.setdefault(case.pair_id, []).append(case)
    for pair_id, members in pairs.items():
        if len(members) != 2:
            raise ValueError(f"{pair_id}: each controlled pair must contain two cases")
        left, right = members
        if left.intent != right.intent or left.actions != right.actions:
            raise ValueError(f"{pair_id}: paired cases must share intent and actions")
        if left.state == right.state:
            raise ValueError(f"{pair_id}: paired cases must have different states")


def _ordering(case: BenchmarkCase, ranking: list[RankedAction]) -> float | None:
    scores = {item.action: item.probability for item in ranking}
    comparisons = [
        scores[preferred] > scores[other]
        for index, tier in enumerate(case.expected_tiers)
        for later in case.expected_tiers[index + 1 :]
        for preferred in tier
        for other in later
    ]
    return sum(comparisons) / len(comparisons) if comparisons else None


def _evaluate(case: BenchmarkCase, evaluator: SystemOneEvaluator) -> CaseResult:
    started = perf_counter()
    try:
        ranking = rank_actions(
            case.intent, case.state, case.actions, evaluator=evaluator
        )
    except (SystemOneError, InvalidEvaluationError) as error:
        return CaseResult(
            case.id,
            case.pair_id,
            [],
            None,
            perf_counter() - started,
            f"{type(error).__name__}: {error}",
        )
    model = getattr(evaluator, "model", None) if case.actions else None
    result = CaseResult(
        case.id,
        case.pair_id,
        ranking,
        model if isinstance(model, str) else None,
        perf_counter() - started,
        None,
    )
    result.pairwise_ordering_accuracy = _ordering(case, ranking)
    if case.relevant_actions:
        result.top_action_relevant = ranking[0].action in case.relevant_actions
    if ranking:
        result.max_probability = ranking[0].probability
    return result


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _metrics(results: list[CaseResult]) -> dict[str, object]:
    orderings = [
        result.pairwise_ordering_accuracy
        for result in results
        if result.pairwise_ordering_accuracy is not None
    ]
    top = [
        float(result.top_action_relevant)
        for result in results
        if result.top_action_relevant is not None
    ]
    return {
        "total_cases": len(results),
        "error_cases": sum(result.error is not None for result in results),
        "comparable_cases": len(orderings),
        "noncomparable_successful_cases": sum(
            result.error is None and result.pairwise_ordering_accuracy is None
            for result in results
        ),
        "pairwise_ordering_accuracy": _mean(orderings),
        "top_action_relevance": _mean(top),
        "top_action_evaluated_cases": len(top),
    }


def _pairs(results: list[CaseResult]) -> list[dict[str, object]]:
    pairs: dict[str, list[CaseResult]] = {}
    for result in results:
        if result.pair_id is not None:
            pairs.setdefault(result.pair_id, []).append(result)
    return [
        {
            "pair_id": pair_id,
            "passed": len(members) == 2
            and all(
                member.error is None and member.pairwise_ordering_accuracy == 1.0
                for member in members
            ),
        }
        for pair_id, members in pairs.items()
    ]


def run_benchmark(
    cases: list[BenchmarkCase],
    *,
    evaluator: SystemOneEvaluator,
) -> dict[str, object]:
    """Evaluate cases and return JSON-ready scores, errors, and label comparisons.

    Labels never enter evaluator requests. Errors are excluded from score averages
    and counted separately. No probability threshold is assumed for abstention.
    """
    results = [_evaluate(case, evaluator) for case in cases]
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "metrics": _metrics(results),
        "pairs": _pairs(results),
        "results": [asdict(result) for result in results],
    }
