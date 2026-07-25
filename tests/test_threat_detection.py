import asyncio
import json
from collections.abc import Awaitable, Callable

from npc.experiments.threat_detection import (
    CandidateThreat,
    build_threat_sensor_prompt,
    perceive_threat,
)


def candidate(threat: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({"threat": threat, "certainty": certainty, "evidence": evidence})


def completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def test_shared_detector_parses_and_validates_the_binary_contract() -> None:
    result = asyncio.run(
        perceive_threat(
            "Leave the fox alone, or I will hurt you.",
            "fox",
            completion(candidate(True, 0.7, "I will hurt you")),
        )
    )

    assert result.candidate == CandidateThreat(True, 0.7, "I will hurt you")
    assert result.validation_result == "accepted"


def test_target_specific_prompt_is_a_single_player_text_question_without_action_or_world_instruction() -> None:
    prompt = build_threat_sensor_prompt("fox")

    assert "credible hostile threat toward the fox" in prompt
    assert "exactly `threat`, `certainty`, and `evidence`" in prompt
    assert "world" not in prompt.lower()
    assert "action" not in prompt.lower()


def test_shared_detector_rejects_malformed_and_ungrounded_true_candidates() -> None:
    malformed = asyncio.run(perceive_threat("I will hurt you.", "wolf", completion("not json")))
    ungrounded = asyncio.run(perceive_threat("I will hurt you.", "wolf", completion(candidate(True, 0.7, "I own this forest"))))

    assert malformed.validation_result == "invalid_candidate"
    assert ungrounded.validation_result == "evidence_not_in_player_message"
