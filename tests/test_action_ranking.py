"""Public ranking contracts, independent of a live model."""

import json
from collections.abc import Sequence

import pytest

from npc.action_ranking import InvalidEvaluationError, Question, rank_actions

NONSTRING_VALUES: tuple[object, ...] = (None, 1, [])


class Evaluator:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[dict[str, str], dict[str, Question]]] = []

    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        self.calls.append((state, questions))
        return self.response


def response(*scores: object) -> dict[str, object]:
    return {
        "answers": {
            f"action_{i}": {"type": "noul", "noul": score}
            for i, score in enumerate(scores)
        }
    }


def test_batch_mapping_and_stable_sort() -> None:
    """Every candidate is scored in one batch; ties preserve original identity."""
    evaluator = Evaluator(response(0.2, 0.9, 0.9))
    names = ["send_invoice", 'read_"logs"', "inspect_metrics"]
    result = rank_actions(
        " Restore service ", " Errors observed ", names, evaluator=evaluator
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
    ("intent", "state", "actions"),
    [
        (" ", "state", ["a"]),
        ("goal", "\n", ["a"]),
        ("goal", "state", [" "]),
        ("goal", "state", ["a", "a"]),
        ("", "state", []),
        ("goal", "state", "action"),
        *[(value, "state", ["a"]) for value in NONSTRING_VALUES],
        *[("goal", value, ["a"]) for value in NONSTRING_VALUES],
        *[("goal", "state", [value]) for value in NONSTRING_VALUES],
        ("goal", "state", ["a", " a "]),
    ],
)
def test_invalid_inputs_avoid_evaluation(
    intent: str,
    state: str,
    actions: Sequence[str],
) -> None:
    """Caller errors fail before consuming model resources, even with no actions."""
    evaluator = Evaluator(response())
    with pytest.raises(ValueError):
        rank_actions(intent, state, actions, evaluator=evaluator)
    assert evaluator.calls == []


def test_trimmed_tuple_actions_map_answers_by_id() -> None:
    """Sequence inputs yield trimmed names with scores matched by ID, not position."""
    evaluator = Evaluator(
        {
            "answers": {
                "action_1": {"type": "noul", "noul": 0.9},
                "action_0": {"type": "noul", "noul": 0.2},
            }
        }
    )
    result = rank_actions(
        "goal", "state", (" inspect_logs \n", " restart_service "), evaluator=evaluator
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
    evaluator = Evaluator(None)
    assert rank_actions("goal", "state", [], evaluator=evaluator) == []
    assert evaluator.calls == []


def test_action_limit_accepts_ten() -> None:
    """The maximum catalog is fully ranked rather than rejected or truncated."""
    names = [f"action_{index}" for index in range(10)]
    evaluator = Evaluator(response(*([0.5] * 10)))
    result = rank_actions("goal", "state", names, evaluator=evaluator)
    assert [(item.action, item.probability) for item in result] == [
        (name, 0.5) for name in names
    ]
    assert len(evaluator.calls) == 1


def test_action_limit_rejects_eleven() -> None:
    """Oversized catalogs fail as caller errors before consuming model resources."""
    evaluator = Evaluator(response(*([0.5] * 11)))
    with pytest.raises(ValueError) as error:
        rank_actions(
            "goal",
            "state",
            [f"action_{index}" for index in range(11)],
            evaluator=evaluator,
        )
    assert "11" in str(error.value)
    assert "10" in str(error.value)
    assert evaluator.calls == []


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"answers": []},
        {"answers": {}},
        {"answers": {"action_0": {"type": "choice", "noul": 0.5}}},
        {"answers": {"action_0": {"noul": 0.5}}},
        {"answers": {"action_0": None}},
        {"answers": {"action_0": {"type": "noul"}}},
        response(0.5, 0.8),
    ],
)
def test_invalid_answer_contract(payload: object) -> None:
    """Wrong shapes, missing answers and extra IDs invalidate the entire result."""
    with pytest.raises(InvalidEvaluationError):
        rank_actions("goal", "state", ["a"], evaluator=Evaluator(payload))


def test_boundary_probabilities() -> None:
    """Zero and one are valid probabilities and remain unnormalized."""
    result = rank_actions(
        "goal", "state", ["a", "b", "c"], evaluator=Evaluator(response(0, 1, 1))
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
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            raise RuntimeError("dependency unavailable")

    with pytest.raises(RuntimeError, match="dependency unavailable"):
        rank_actions("goal", "state", ["a"], evaluator=Broken())
