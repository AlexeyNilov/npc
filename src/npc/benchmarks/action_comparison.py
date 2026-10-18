"""Compare independent relevance and comparative choice on the same cases."""

from typing import TypedDict, cast

from npc.action_ranking import CHOICE_PROMPT_VERSION, rank_actions_by_choice
from npc.benchmarks.action_ranking import BenchmarkCase, run_benchmark
from npc.benchmarks.runner import USEFULNESS_THRESHOLD, Case, observe_cases
from npc.model.evaluation import ChoiceEvaluator, Evaluator


class Prediction(TypedDict):
    """One serialized action probability."""

    action: str
    probability: float


class Observation(TypedDict):
    """Fields needed to compare rankings independently of score calibration."""

    id: str
    ranking: list[Prediction]
    error: str | None


def _reciprocal_rank(row: Observation, labels: list[str]) -> float:
    return next(
        (
            1 / position
            for position, item in enumerate(row["ranking"], 1)
            if item["action"] in labels
        ),
    )


def _comparison(
    cases: list[BenchmarkCase], noul: list[Observation], choice: list[Observation]
) -> dict[str, int | float | None]:
    pairs = [
        (
            _reciprocal_rank(left, case.relevant_actions),
            _reciprocal_rank(right, case.relevant_actions),
        )
        for case, left, right in zip(cases, noul, choice, strict=True)
        if case.relevant_actions and left["error"] is None and right["error"] is None
    ]
    count = len(pairs)
    return {
        "paired_cases": count,
        "noul_top1_accuracy": sum(left == 1 for left, _ in pairs) / count
        if count
        else None,
        "choice_top1_accuracy": sum(right == 1 for _, right in pairs) / count
        if count
        else None,
        "noul_mean_reciprocal_rank": sum(left for left, _ in pairs) / count
        if count
        else None,
        "choice_mean_reciprocal_rank": sum(right for _, right in pairs) / count
        if count
        else None,
        "noul_only_correct": sum(left == 1 and right != 1 for left, right in pairs),
        "choice_only_correct": sum(right == 1 and left != 1 for left, right in pairs),
        "both_correct": sum(left == right == 1 for left, right in pairs),
        "neither_correct": sum(left != 1 and right != 1 for left, right in pairs),
        "no_relevant_cases": sum(not case.relevant_actions for case in cases),
        "empty_catalog_cases": sum(not case.actions for case in cases),
        "noul_no_relevant_abstentions": sum(
            not case.relevant_actions
            and bool(case.actions)
            and row["error"] is None
            and all(
                item["probability"] < USEFULNESS_THRESHOLD for item in row["ranking"]
            )
            for case, row in zip(cases, noul, strict=True)
        ),
        "choice_no_relevant_forced_choices": sum(
            not case.relevant_actions and bool(row["ranking"]) and row["error"] is None
            for case, row in zip(cases, choice, strict=True)
        ),
    }


def run_comparison(
    cases: list[BenchmarkCase],
    *,
    evaluator: Evaluator,
    choice_evaluator: ChoiceEvaluator,
) -> dict[str, object]:
    """Run noul then choice, preserving native noul scoring and raw choice results.

    Rank metrics use only cases with a relevant action and two successful requests.
    Empty and no-relevant catalogs are counted separately. Labels stay local.
    Each approach retains its model, prompt version, elapsed time, and errors.
    """
    noul = run_benchmark(cases, evaluator=evaluator)
    results, model, elapsed = observe_cases(
        [
            Case(case.id, case.state, case.actions, case.relevant_actions)
            for case in cases
        ],
        predict=lambda case: [
            (item.action, item.probability)
            for item in rank_actions_by_choice(
                case.state, case.candidates, evaluator=choice_evaluator
            )
        ],
        evaluator=choice_evaluator,
    )
    choice_rows = [
        {
            "id": result.case.id,
            "state": result.case.state,
            "actions": result.case.candidates,
            "relevant_actions": result.case.labels,
            "ranking": [
                {"action": name, "probability": score} for name, score in result.ranking
            ],
            "elapsed_seconds": result.elapsed_seconds,
            "error": result.error,
        }
        for result in results
    ]
    return {
        "benchmark": "action-ranking-comparison",
        "dataset_hash": noul["dataset_hash"],
        "created_at": noul["created_at"],
        "noul": noul,
        "choice": {
            "model": model,
            "prompt_version": CHOICE_PROMPT_VERSION,
            "elapsed_seconds": elapsed,
            "metrics": {
                "request_error_cases": sum(
                    result.error is not None for result in results
                )
            },
            "results": choice_rows,
        },
        "comparison": _comparison(
            cases,
            cast(list[Observation], noul["results"]),
            cast(list[Observation], choice_rows),
        ),
    }
