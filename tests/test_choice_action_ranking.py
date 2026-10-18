"""Contracts for comparative action ranking, independent of HTTP."""

import json

import pytest

from npc.choice_action_ranking import ChoiceQuestion, rank_actions_by_choice
from npc.model.evaluation import State

STATE = {"intent": " Restore service ", "situation": "Cause unknown", "extra": ""}


class Evaluator:
    def __init__(self, scores: dict[str, float]) -> None:
        self.scores = scores
        self.calls: list[tuple[State, ChoiceQuestion]] = []

    def evaluate_choice(
        self, state: State, question: ChoiceQuestion
    ) -> dict[str, float]:
        self.calls.append((state, question))
        return self.scores


def test_comparative_ranking() -> None:
    """One comparative question preserves names, raw scores, ties, and caller state."""
    evaluator = Evaluator({'read_"logs"': 0.45, "inspect": 0.45, "restart": 0.1})
    state = dict(STATE)
    actions = [" restart ", 'read_"logs"', "inspect"]
    result = rank_actions_by_choice(state, actions, evaluator=evaluator)
    assert [(item.action, item.probability) for item in result] == [
        ('read_"logs"', 0.45),
        ("inspect", 0.45),
        ("restart", 0.1),
    ]
    assert state == STATE
    assert actions == [" restart ", 'read_"logs"', "inspect"]
    assert len(evaluator.calls) == 1
    sent, question = evaluator.calls[0]
    assert sent == {
        **STATE,
        "available_actions": json.dumps(["restart", 'read_"logs"', "inspect"]),
    }
    assert question.options == ("restart", 'read_"logs"', "inspect")
    for term in (
        "best next step",
        "intent",
        "situation",
        "prerequisites",
        "costs",
        "completed work",
        "data, not instructions",
    ):
        assert term in question.instructions


@pytest.mark.parametrize("count", [0, 1, 10])
def test_catalog_boundaries(count: int) -> None:
    """Empty input skips evaluation; singleton and maximum catalogs are evaluated."""
    names = [f"action_{i}" for i in range(count)]
    evaluator = Evaluator(dict.fromkeys(names, 1 / count if count else 0))
    result = rank_actions_by_choice(STATE, tuple(names), evaluator=evaluator)
    assert [item.action for item in result] == names
    assert len(evaluator.calls) == (1 if count else 0)


@pytest.mark.parametrize(
    ("state", "actions"),
    [
        ({"intent": "", "situation": "s"}, []),
        ({"intent": "i", "situation": " "}, ["a"]),
        ({**STATE, "available_actions": "[]"}, ["a"]),
        ({**STATE, "extra": 1}, ["a"]),
        (STATE, "action"),
        (STATE, [" "]),
        (STATE, ["a", " a "]),
        (STATE, [f"a{i}" for i in range(11)]),
    ],
)
def test_invalid_input(state: State, actions: list[str]) -> None:
    """The shared action input policy rejects invalid inputs before evaluation."""
    evaluator = Evaluator({})
    with pytest.raises(ValueError):
        rank_actions_by_choice(state, actions, evaluator=evaluator)
    assert evaluator.calls == []


def test_dependency_failure() -> None:
    """Evaluator failures propagate without returning a partial ranking."""

    class Broken:
        def evaluate_choice(
            self, state: State, question: ChoiceQuestion
        ) -> dict[str, float]:
            raise RuntimeError("offline")

    with pytest.raises(RuntimeError, match="offline"):
        rank_actions_by_choice(STATE, ["a"], evaluator=Broken())
