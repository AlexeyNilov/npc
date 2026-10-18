"""Public contracts for ranking complete plans supplied as short texts."""

import json
from collections.abc import Sequence

import pytest

from npc.model.evaluation import Question, State
from npc.plan_ranking import rank_plans


class Evaluator:
    def __init__(self, payload: dict[str, float]) -> None:
        self.payload = payload
        self.calls: list[tuple[State, dict[str, Question]]] = []

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        self.calls.append((state, questions))
        return self.payload


def response(*scores: float) -> dict[str, float]:
    return {f"plan_{i}": score for i, score in enumerate(scores)}


def test_rank_complete_plans_in_one_batch() -> None:
    """Whole plans get raw scores by ID, with stable ties and no text rewriting."""
    plans = (
        " Restart now; investigate later. ",
        'Read "logs". Fix the cause.\nVerify checkout.',
        "Roll back the failed release, then verify checkout.",
    )
    evaluator = Evaluator(response(0.2, 0.9, 0.9))
    ranking = rank_plans(
        {"intent": " Restore checkout ", "situation": " Cause unknown "},
        plans,
        evaluator=evaluator,
    )
    assert [(item.plan, item.probability) for item in ranking] == [
        (plans[1], 0.9),
        (plans[2], 0.9),
        (plans[0].strip(), 0.2),
    ]
    assert len(evaluator.calls) == 1
    context, questions = evaluator.calls[0]
    assert context == {
        "intent": " Restore checkout ",
        "situation": " Cause unknown ",
        "available_plans": json.dumps([plan.strip() for plan in plans]),
    }
    assert set(questions) == {"plan_0", "plan_1", "plan_2"}
    for i, plan in enumerate(plans):
        question = questions[f"plan_{i}"]
        assert question["type"] == "noul"
        instructions = question["instructions"]
        assert json.dumps(plan.strip()) in instructions
        for concept in (
            "complete plan",
            "feasib",
            "order",
            "prerequisite",
            "cost",
            "completed work",
            "data, not instructions",
        ):
            assert concept in instructions


@pytest.mark.parametrize(
    ("intent", "situation", "plans"),
    [
        ("", "circumstances", []),
        ("goal", " ", ["plan"]),
        ("goal", "circumstances", "plan"),
        ("goal", "circumstances", [" "]),
        ("goal", "circumstances", ["plan", " plan "]),
        ("goal", "circumstances", [str(i) for i in range(11)]),
        (None, "circumstances", ["plan"]),
        ("goal", None, ["plan"]),
        ("goal", "circumstances", [None]),
    ],
)
def test_invalid_input_avoids_evaluation(
    intent: str, situation: str, plans: Sequence[str]
) -> None:
    """Invalid context and catalogs fail before consuming model resources."""
    evaluator = Evaluator({})
    with pytest.raises(ValueError):
        rank_plans(
            {"intent": intent, "situation": situation}, plans, evaluator=evaluator
        )
    assert evaluator.calls == []


def test_empty_plans_avoid_evaluation() -> None:
    """An empty catalog yields no recommendation and requires no dependency."""
    evaluator = Evaluator({})
    assert (
        rank_plans(
            {"intent": "goal", "situation": "circumstances"}, [], evaluator=evaluator
        )
        == []
    )
    assert evaluator.calls == []


def test_ten_plans_and_boundary_scores() -> None:
    """The full supported catalog is returned without normalization or truncation."""
    plans = [str(i) for i in range(10)]
    ranking = rank_plans(
        {"intent": "goal", "situation": "circumstances"},
        plans,
        evaluator=Evaluator(response(0, *([1] * 9))),
    )
    assert [(item.plan, item.probability) for item in ranking] == [
        *((plan, 1) for plan in plans[1:]),
        ("0", 0),
    ]


def test_dependency_failure_propagates() -> None:
    """Dependency errors remain distinguishable from invalid model responses."""

    class Broken:
        def evaluate(
            self, state: State, questions: dict[str, Question]
        ) -> dict[str, float]:
            raise RuntimeError("unavailable")

    with pytest.raises(RuntimeError, match="unavailable"):
        rank_plans(
            {"intent": "goal", "situation": "circumstances"},
            ["plan"],
            evaluator=Broken(),
        )
