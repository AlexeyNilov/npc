"""Shared state contracts exposed by both public rankers."""

from collections.abc import Sequence
from typing import Protocol

import pytest

from npc.action_ranking import RankedAction, rank_actions_by_relevance
from npc.model.evaluation import Evaluator, Question, State
from npc.plan_ranking import RankedPlan, rank_plans


class Ranker(Protocol):
    def __call__(
        self, state: State, candidates: Sequence[str], /, *, evaluator: Evaluator
    ) -> Sequence[RankedAction | RankedPlan]: ...


class RecordingEvaluator:
    def __init__(self) -> None:
        self.calls: list[State] = []

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        self.calls.append(state)
        return {key: 0.8 for key in questions}


@pytest.mark.parametrize(
    ("rank", "catalog"),
    [(rank_actions_by_relevance, "available_actions"), (rank_plans, "available_plans")],
)
def test_extended_state_is_preserved_without_mutation(
    rank: Ranker, catalog: str
) -> None:
    """New context fields reach evaluation without changing caller-owned state."""
    state = {
        "intent": " Restore checkout ",
        "situation": " Cause unknown ",
        "recent_events": "A release just completed.",
        "constraints": "",
    }
    original = state.copy()
    evaluator = RecordingEvaluator()
    ranking = rank(state, [" inspect_logs "], evaluator=evaluator)
    assert len(ranking) == 1
    assert evaluator.calls == [{**original, catalog: '["inspect_logs"]'}]
    assert state == original


@pytest.mark.parametrize("rank", [rank_actions_by_relevance, rank_plans])
@pytest.mark.parametrize(
    "state",
    [
        None,
        "situation",
        [],
        {},
        {"intent": "goal"},
        {"situation": "circumstances"},
        {"intent": " ", "situation": "circumstances"},
        {"intent": "goal", "situation": " "},
        {"intent": None, "situation": "circumstances"},
        {"intent": "goal", "situation": "circumstances", "extra": 1},
        {"intent": "goal", "situation": "circumstances", 1: "extra"},
    ],
)
def test_invalid_state_fails_before_evaluation(rank: Ranker, state: State) -> None:
    """Malformed state fails even when an empty catalog avoids evaluation."""
    evaluator = RecordingEvaluator()
    with pytest.raises(ValueError):
        rank(state, [], evaluator=evaluator)
    assert evaluator.calls == []


@pytest.mark.parametrize(
    ("rank", "catalog"),
    [(rank_actions_by_relevance, "available_actions"), (rank_plans, "available_plans")],
)
@pytest.mark.parametrize("candidates", [[], ["inspect_logs"]])
def test_catalog_conflict_is_rejected(
    rank: Ranker, catalog: str, candidates: list[str]
) -> None:
    """A caller cannot supply a catalog that conflicts with the ranked candidates."""
    state = {"intent": "goal", "situation": "circumstances", catalog: "[]"}
    evaluator = RecordingEvaluator()
    with pytest.raises(ValueError):
        rank(state, candidates, evaluator=evaluator)
    assert evaluator.calls == []
