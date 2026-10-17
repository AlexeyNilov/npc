"""Shared typed-question evaluator contract and response decoding."""

from typing import Protocol, TypedDict


class Question(TypedDict):
    """A System One probability-of-true question."""

    type: str
    instructions: str


class SystemOneEvaluator(Protocol):
    """Evaluate typed questions without coupling ranking to a transport."""

    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        """Return answers with finite numeric noul probabilities in [0, 1]."""
        ...


class InvalidEvaluationError(ValueError):
    """The evaluator returned an invalid answer structure or mismatched IDs."""


def _probability(answer: object) -> float:
    if not isinstance(answer, dict) or answer.get("type") != "noul":
        raise InvalidEvaluationError("Each answer must have type noul")
    if "noul" not in answer:
        raise InvalidEvaluationError("Each answer must include a noul probability")
    return float(answer["noul"])


def probabilities(payload: object, questions: dict[str, Question]) -> dict[str, float]:
    """Decode exactly the requested answers, trusting upstream numeric guarantees."""
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
        raise InvalidEvaluationError("Expected an answers mapping")
    answers: dict[str, object] = payload["answers"]
    if answers.keys() != questions.keys():
        raise InvalidEvaluationError("Answer IDs must match all requested question IDs")
    return {key: _probability(answers[key]) for key in questions}
