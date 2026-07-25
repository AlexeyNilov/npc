import asyncio
import json
from collections.abc import Awaitable, Callable

from npc.experiments.food_offer_detection import (
    CandidateFoodOffer,
    build_food_offer_sensor_prompt,
    perceive_food_offer,
)


def candidate(food_offer: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({"food_offer": food_offer, "certainty": certainty, "evidence": evidence})


def completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def test_food_offer_detector_parses_and_validates_an_explicit_grounded_offer() -> None:
    result = asyncio.run(
        perceive_food_offer(
            "Wolf, I offer you this fresh meat.",
            "wolf",
            completion(candidate(True, 0.7, "I offer you this fresh meat")),
        )
    )

    assert result.candidate == CandidateFoodOffer(True, 0.7, "I offer you this fresh meat")
    assert result.validation_result == "accepted"


def test_food_offer_prompt_is_one_player_text_question_without_action_world_or_dialogue() -> None:
    prompt = build_food_offer_sensor_prompt("wolf")

    assert "explicitly offer food to the wolf" in prompt
    assert "exactly `food_offer`, `certainty`, and `evidence`" in prompt
    assert "action" not in prompt.lower()
    assert "world" not in prompt.lower()
    assert "dialogue" not in prompt.lower()


def test_food_offer_detector_rejects_malformed_invalid_certainty_empty_and_ungrounded_candidates() -> None:
    player_message = "Wolf, I offer you this fresh meat."
    cases = (
        ("not json", "invalid_candidate"),
        (candidate(True, 1.1, "I offer you this fresh meat"), "certainty_out_of_range"),
        (candidate(True, 0.7, ""), "evidence_empty"),
        (candidate(True, 0.7, "I offer you a rabbit"), "evidence_not_in_player_message"),
    )

    for raw_candidate, expected_validation in cases:
        result = asyncio.run(perceive_food_offer(player_message, "wolf", completion(raw_candidate)))
        assert result.validation_result == expected_validation
