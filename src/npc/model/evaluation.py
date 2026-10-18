"""Questions and the domain contract for evaluating their probabilities."""

from dataclasses import dataclass
from typing import Protocol, TypedDict

type State = dict[str, str]
"""Complete content evaluated against questions, with extensible named text fields.

Required fields belong to each caller's contract, not to the evaluator.
"""


def validate_state(state: State) -> None:
    """Require a mapping of string keys to string values, allowing empty text.

    Raises:
        ValueError: State is not a dict or contains a nonstring key or value.
    """
    if not isinstance(state, dict):
        raise ValueError("state must be an object with string keys and values")
    for key, value in state.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("state keys and values must be strings")


def validate_ranking_state(state: State, catalog: str) -> None:
    """Require ranking context and reserve the catalog field supplied by a ranker."""
    validate_state(state)
    for field in ("intent", "situation"):
        if not state.get(field, "").strip():
            raise ValueError("intent and situation must be nonblank strings")
    if catalog in state:
        raise ValueError(f"state must omit {catalog}; the ranker supplies it")


class Question(TypedDict):
    """A probability-of-true question."""

    type: str
    instructions: str


class Evaluator(Protocol):
    """Evaluate questions against a state without coupling callers to a provider."""

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        """Return exactly the requested IDs with finite probabilities in [0, 1]."""
        ...


@dataclass(frozen=True)
class ChoiceQuestion:
    """Instructions and ordered action options for a comparative decision."""

    instructions: str
    options: tuple[str, ...]


class ChoiceEvaluator(Protocol):
    """Evaluate one choice without exposing provider request types."""

    def evaluate_choice(
        self, state: State, question: ChoiceQuestion
    ) -> dict[str, float]:
        """Return exactly the option names with finite probabilities totaling one."""
        ...
