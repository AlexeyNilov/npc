"""Questions and the domain contract for evaluating their probabilities."""

from typing import Protocol, TypedDict


class Question(TypedDict):
    """A probability-of-true question."""

    type: str
    instructions: str


class Evaluator(Protocol):
    """Evaluate questions against a state without coupling callers to a provider."""

    def evaluate(
        self, state: dict[str, str], questions: dict[str, Question]
    ) -> dict[str, float]:
        """Return exactly the requested IDs with finite probabilities in [0, 1]."""
        ...
