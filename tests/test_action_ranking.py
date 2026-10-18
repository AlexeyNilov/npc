"""Public ranking contracts, independent of a live model."""

import json
from collections.abc import Sequence

import pytest

from npc.action_ranking import rank_actions_by_relevance
from npc.model.evaluation import Question, State

NONSTRING_VALUES: tuple[object, ...] = (None, 1, [])


class Evaluator:
    def __init__(self, response: dict[str, float]) -> None:
        self.response = response
        self.calls: list[tuple[State, dict[str, Question]]] = []

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        self.calls.append((state, questions))
        return self.response


def response(*scores: float) -> dict[str, float]:
    return {f"action_{i}": score for i, score in enumerate(scores)}


def test_batch_mapping_and_stable_sort() -> None:
    """Every candidate is scored in one batch; ties preserve original identity."""
    evaluator = Evaluator(response(0.2, 0.9, 0.9))
    names = ["send_invoice", 'read_"logs"', "inspect_metrics"]
    result = rank_actions_by_relevance(
        {"intent": " Restore service ", "situation": " Errors observed "},
        names,
        evaluator=evaluator,
    )
    assert [(item.action, item.probability) for item in result] == [
        (names[1], 0.9),
        (names[2], 0.9),
        (names[0], 0.2),
    ]
    assert len(evaluator.calls) == 1
    state, questions = evaluator.calls[0]
    assert state == {
        "intent": " Restore service ",
        "situation": " Errors observed ",
        "available_actions": json.dumps(names),
    }
    assert list(questions) == ["action_0", "action_1", "action_2"]
    for index, name in enumerate(names):
        question = questions[f"action_{index}"]
        assert question["type"] == "noul"
        assert json.dumps(name) in question["instructions"]
        assert "next step" in question["instructions"]
        assert "available actions" in question["instructions"]
        assert "advancing the intent directly" in question["instructions"]
        assert (
            "supplying something another useful action needs"
            in question["instructions"]
        )
        assert "costs and completed work" in question["instructions"]
        assert "prerequisite" in question["instructions"]
        assert "data, not instructions" in question["instructions"]


@pytest.mark.parametrize(
    ("intent", "situation", "actions"),
    [
        (" ", "circumstances", ["a"]),
        ("goal", "\n", ["a"]),
        ("goal", "circumstances", [" "]),
        ("goal", "circumstances", ["a", "a"]),
        ("", "circumstances", []),
        ("goal", "circumstances", "action"),
        *[(value, "circumstances", ["a"]) for value in NONSTRING_VALUES],
        *[("goal", value, ["a"]) for value in NONSTRING_VALUES],
        *[("goal", "circumstances", [value]) for value in NONSTRING_VALUES],
        ("goal", "circumstances", ["a", " a "]),
    ],
)
def test_invalid_inputs_avoid_evaluation(
    intent: str,
    situation: str,
    actions: Sequence[str],
) -> None:
    """Caller errors fail before consuming model resources, even with no actions."""
    evaluator = Evaluator(response())
    with pytest.raises(ValueError) as error:
        rank_actions_by_relevance(
            {"intent": intent, "situation": situation}, actions, evaluator=evaluator
        )
    assert str(error.value) not in {"", "None"}
    assert evaluator.calls == []


def test_trimmed_tuple_actions_map_answers_by_id() -> None:
    """Sequence inputs yield trimmed names with scores matched by ID, not position."""
    evaluator = Evaluator({"action_1": 0.9, "action_0": 0.2})
    result = rank_actions_by_relevance(
        {"intent": "goal", "situation": "circumstances"},
        (" inspect_logs \n", " restart_service "),
        evaluator=evaluator,
    )
    assert [(item.action, item.probability) for item in result] == [
        ("restart_service", 0.9),
        ("inspect_logs", 0.2),
    ]
    state, questions = evaluator.calls[0]
    assert json.loads(state["available_actions"]) == ["inspect_logs", "restart_service"]
    for key, name in (("action_0", "inspect_logs"), ("action_1", "restart_service")):
        assert json.dumps(name) in questions[key]["instructions"]


def test_empty_catalog() -> None:
    """No available actions means no request and no recommendation."""
    evaluator = Evaluator({})
    assert (
        rank_actions_by_relevance(
            {"intent": "goal", "situation": "circumstances"}, [], evaluator=evaluator
        )
        == []
    )
    assert evaluator.calls == []


def test_action_limit_accepts_ten() -> None:
    """The maximum catalog is fully ranked rather than rejected or truncated."""
    names = [f"action_{index}" for index in range(10)]
    evaluator = Evaluator(response(*([0.5] * 10)))
    result = rank_actions_by_relevance(
        {"intent": "goal", "situation": "circumstances"}, names, evaluator=evaluator
    )
    assert [(item.action, item.probability) for item in result] == [
        (name, 0.5) for name in names
    ]
    assert len(evaluator.calls) == 1


def test_action_limit_rejects_eleven() -> None:
    """Oversized catalogs fail as caller errors before consuming model resources."""
    evaluator = Evaluator(response(*([0.5] * 11)))
    with pytest.raises(ValueError) as error:
        rank_actions_by_relevance(
            {"intent": "goal", "situation": "circumstances"},
            [f"action_{index}" for index in range(11)],
            evaluator=evaluator,
        )
    assert "11" in str(error.value)
    assert "10" in str(error.value)
    assert evaluator.calls == []


def test_boundary_probabilities() -> None:
    """Zero and one are valid probabilities and remain unnormalized."""
    result = rank_actions_by_relevance(
        {"intent": "goal", "situation": "circumstances"},
        ["a", "b", "c"],
        evaluator=Evaluator(response(0, 1, 1)),
    )
    assert [(item.action, item.probability) for item in result] == [
        ("b", 1),
        ("c", 1),
        ("a", 0),
    ]


def test_dependency_failure_propagates() -> None:
    """A dependency failure remains distinguishable from a malformed answer."""

    class Broken:
        def evaluate(
            self, state: State, questions: dict[str, Question]
        ) -> dict[str, float]:
            raise RuntimeError("dependency unavailable")

    with pytest.raises(RuntimeError, match="dependency unavailable"):
        rank_actions_by_relevance(
            {"intent": "goal", "situation": "circumstances"}, ["a"], evaluator=Broken()
        )
