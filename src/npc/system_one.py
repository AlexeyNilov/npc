"""Synchronous System One HTTP adapter backed by HTTPX2."""

import math
from urllib.parse import urlsplit

import httpx2

from npc.model.evaluation import Question, State


class InvalidEvaluationError(ValueError):
    """The evaluator returned an invalid answer structure or mismatched IDs."""


def _probability(answer: object) -> float:
    if not isinstance(answer, dict) or answer.get("type") != "noul":
        raise InvalidEvaluationError("Each answer must have type noul")
    if "noul" not in answer:
        raise InvalidEvaluationError("Each answer must include a noul probability")
    return float(answer["noul"])


def _probabilities(payload: object, questions: dict[str, Question]) -> dict[str, float]:
    """Decode exactly the requested answers, trusting upstream numeric guarantees."""
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
        raise InvalidEvaluationError("Expected an answers mapping")
    answers: dict[str, object] = payload["answers"]
    if answers.keys() != questions.keys():
        raise InvalidEvaluationError("Answer IDs must match all requested question IDs")
    return {key: _probability(answers[key]) for key in questions}


class SystemOneError(RuntimeError):
    """A System One request failed at the HTTP or JSON boundary."""


def validate_endpoint(endpoint: str) -> str:
    """Require a complete HTTP(S) endpoint, preserving the supplied URL."""
    try:
        url = urlsplit(endpoint)
        valid = url.scheme in {"http", "https"} and bool(url.hostname)
        _ = url.port
    except ValueError as error:
        raise ValueError("SYSTEM_ONE must be an absolute HTTP or HTTPS URL") from error
    if not valid or any(character.isspace() for character in endpoint):
        raise ValueError("SYSTEM_ONE must be an absolute HTTP or HTTPS URL")
    return endpoint


class SystemOneClient:
    """Evaluate questions using a caller-owned reusable HTTPX2 client.

    The caller closes the injected client. The endpoint is a complete URL;
    the adapter adds no path. Model metadata describes the latest response.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        client: httpx2.Client,
        timeout: float = 30.0,
    ) -> None:
        self.endpoint = validate_endpoint(endpoint)
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        self.client = client
        self.timeout = timeout
        self.model: str | None = None

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        """POST one batch and decode domain probabilities, preserving dependency failures."""
        self.model = None
        try:
            response = self.client.post(
                self.endpoint,
                json={"state": state, "questions": questions},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload: object = response.json()
        except httpx2.HTTPStatusError as error:
            raise SystemOneError(
                f"System One HTTP {error.response.status_code}"
            ) from error
        except httpx2.RequestError as error:
            raise SystemOneError(
                f"System One request failed ({type(error).__name__})"
            ) from error
        except ValueError as error:
            raise SystemOneError("System One returned invalid JSON") from error
        if isinstance(payload, dict) and isinstance(payload.get("model"), str):
            self.model = payload["model"]
        return _probabilities(payload, questions)
