"""System One choice adapter, isolated from the existing noul adapter."""

import math

import httpx2

from npc.choice_action_ranking import ChoiceQuestion
from npc.model.evaluation import State
from npc.system_one import InvalidEvaluationError, SystemOneError, validate_endpoint


def _decode(payload: object, options: tuple[str, ...]) -> dict[str, float]:
    """Match external question and option identities; trust numeric guarantees."""
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
        raise InvalidEvaluationError("Expected an answers mapping")
    answers = payload["answers"]
    if answers.keys() != {"action_choice"}:
        raise InvalidEvaluationError(
            "Answer IDs must match the requested choice question"
        )
    answer = answers["action_choice"]
    if not isinstance(answer, dict) or answer.get("type") != "choice":
        raise InvalidEvaluationError("Expected a choice answer")
    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict) or probabilities.keys() != {
        f"action_{i}" for i in range(len(options))
    }:
        raise InvalidEvaluationError(
            "Probabilities must match all requested option IDs"
        )
    return {name: float(probabilities[f"action_{i}"]) for i, name in enumerate(options)}


class SystemOneChoiceClient:
    """Evaluate one comparative question using a caller-owned HTTPX2 client.

    The caller closes the injected client. The endpoint is a complete URL;
    no path is added. Model metadata describes the latest response.
    """

    def __init__(
        self, endpoint: str, *, client: httpx2.Client, timeout: float = 30.0
    ) -> None:
        self.endpoint = validate_endpoint(endpoint)
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        self.client = client
        self.timeout = timeout
        self.model: str | None = None

    def evaluate_choice(
        self, state: State, question: ChoiceQuestion
    ) -> dict[str, float]:
        """POST one choice and return raw probabilities keyed by option name.

        Questions from the ranker contain nonempty unique options. HTTP and JSON
        failures raise SystemOneError; mismatched answer identities or structure
        raise InvalidEvaluationError. Numeric guarantees belong to the provider.
        """
        self.model = None
        questions = {
            "action_choice": {
                "type": "choice",
                "instructions": question.instructions,
                "criteria": {
                    f"action_{i}": name for i, name in enumerate(question.options)
                },
            }
        }
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
        return _decode(payload, question.options)
