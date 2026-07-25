import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import cast

from npc.experiments.wolf_sensemaking import (
    FOOD_OFFER_SENSOR_PROMPT,
    THREAT_SENSOR_PROMPT,
    decide_action,
    load_corpus,
    run_case,
)


def candidate(key: str, value: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({key: value, "certainty": certainty, "evidence": evidence})


def test_each_accepted_perception_has_its_own_action_branch_and_threat_has_priority() -> None:
    cases = (
        (
            "I will hurt you.",
            candidate("threat", True, 0.7, "I will hurt you"),
            candidate("food_offer", False, 0.7, None),
            "attack",
        ),
        (
            "Wolf, I offer you this fresh meat.",
            candidate("threat", False, 0.7, None),
            candidate("food_offer", True, 0.7, "I offer you this fresh meat"),
            "approach",
        ),
        ("Hello wolf.", candidate("threat", False, 0.7, None), candidate("food_offer", False, 0.7, None), "do_nothing"),
        (
            "I will hurt you, but I offer you this fresh meat.",
            candidate("threat", True, 0.7, "I will hurt you"),
            candidate("food_offer", True, 0.7, "I offer you this fresh meat"),
            "attack",
        ),
    )

    for player_message, threat_response, food_offer_response, expected_action in cases:
        result = asyncio.run(run_case(player_message, sensor_completion(threat_response, food_offer_response)))
        assert result.action == expected_action

    assert decide_action(True, True) == "attack"
    assert decide_action(False, True) == "approach"
    assert decide_action(False, False) == "do_nothing"


def test_rejected_sensor_cannot_cause_its_action_and_rejected_threat_does_not_suppress_food_offer() -> None:
    offer_message = "Wolf, I offer you this fresh meat."
    rejected_threat = asyncio.run(
        run_case(
            offer_message,
            sensor_completion("not json", candidate("food_offer", True, 0.7, "I offer you this fresh meat")),
        )
    )
    rejected_offer = asyncio.run(
        run_case(
            "Hello wolf.",
            sensor_completion(candidate("threat", False, 0.7, None), candidate("food_offer", True, 0.7, "")),
        )
    )

    assert rejected_threat.threat_perception.validation_result == "invalid_candidate"
    assert rejected_threat.action == "approach"
    assert rejected_offer.food_offer_perception.validation_result == "evidence_empty"
    assert rejected_offer.action == "do_nothing"


def test_malformed_invalid_certainty_empty_and_ungrounded_candidates_from_either_sensor_fail_closed() -> None:
    threat_message = "I will hurt you."
    offer_message = "Wolf, I offer you this fresh meat."
    rejected_threats = (
        "not json",
        candidate("threat", True, 1.1, "I will hurt you"),
        candidate("threat", True, 0.7, ""),
        candidate("threat", True, 0.7, "I own this forest"),
    )
    rejected_offers = (
        "not json",
        candidate("food_offer", True, 1.1, "I offer you this fresh meat"),
        candidate("food_offer", True, 0.7, ""),
        candidate("food_offer", True, 0.7, "I offer you a rabbit"),
    )

    for raw_candidate in rejected_threats:
        result = asyncio.run(
            run_case(
                threat_message,
                sensor_completion(raw_candidate, candidate("food_offer", False, 0.7, None)),
            )
        )
        assert result.threat_perception.validation_result != "accepted"
        assert result.action == "do_nothing"

    for raw_candidate in rejected_offers:
        result = asyncio.run(
            run_case(
                offer_message,
                sensor_completion(candidate("threat", False, 0.7, None), raw_candidate),
            )
        )
        assert result.food_offer_perception.validation_result != "accepted"
        assert result.action == "do_nothing"


def test_wolf_wrapper_calls_each_sensor_once_and_keeps_perceptions_separate() -> None:
    calls: list[str] = []

    async def complete(_: str, prompt: str) -> str:
        calls.append(prompt)
        if "hostile threat" in prompt:
            return candidate("threat", False, 0.5, None)
        return candidate("food_offer", False, 0.5, None)

    result = asyncio.run(run_case("Hello wolf.", complete))

    assert calls == [THREAT_SENSOR_PROMPT, FOOD_OFFER_SENSOR_PROMPT]
    assert result.threat_perception.raw_candidate != ""
    assert result.food_offer_perception.raw_candidate != ""


def test_certainty_is_invariant_and_prompts_do_not_request_action_or_world_facts() -> None:
    low = asyncio.run(
        run_case(
            "Wolf, I offer you this fresh meat.",
            sensor_completion(
                candidate("threat", False, 0.01, None), candidate("food_offer", True, 0.01, "I offer you this fresh meat")
            ),
        )
    )
    high = asyncio.run(
        run_case(
            "Wolf, I offer you this fresh meat.",
            sensor_completion(
                candidate("threat", False, 0.99, None), candidate("food_offer", True, 0.99, "I offer you this fresh meat")
            ),
        )
    )

    assert low.action == high.action == "approach"
    for prompt in (THREAT_SENSOR_PROMPT, FOOD_OFFER_SENSOR_PROMPT):
        assert "action" not in prompt.lower()
        assert "world" not in prompt.lower()
        assert "dialogue" not in prompt.lower()
        assert "state" not in prompt.lower()


def test_checked_in_corpus_has_required_cases_and_expected_trace_values() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "wolf_sensemaking.yaml"
    cases = load_corpus(corpus_path)
    expected_by_id = {case["id"]: case for case in cases}

    assert set(expected_by_id) == {"threat-only", "offer-only", "neither", "both"}
    assert {case["expected_priority"] for case in cases} == {"threat_over_food_offer"}

    for case in cases:
        calls: list[str] = []

        async def complete(_: str, prompt: str) -> str:
            calls.append(prompt)
            return await sensor_completion_for_case(case)("", prompt)

        trace = asyncio.run(
            run_case(
                cast(str, case["player_message"]),
                complete,
                case,
            )
        )
        assert calls == [THREAT_SENSOR_PROMPT, FOOD_OFFER_SENSOR_PROMPT]
        assert trace.expected_threat == case["expected_threat"]
        assert trace.expected_food_offer == case["expected_food_offer"]
        assert trace.expected_action == case["expected_action"]
        assert trace.priority == case["expected_priority"]
        assert trace.action == case["expected_action"]


def sensor_completion(threat_response: str, food_offer_response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, prompt: str) -> str:
        return threat_response if "hostile threat" in prompt else food_offer_response

    return complete


def sensor_completion_for_case(case: dict[str, object]) -> Callable[[str, str], Awaitable[str]]:
    threat = cast(bool, case["expected_threat"])
    food_offer = cast(bool, case["expected_food_offer"])

    return sensor_completion(
        candidate("threat", threat, 0.5, "I will hurt you" if threat else None),
        candidate("food_offer", food_offer, 0.5, "I offer you this fresh meat" if food_offer else None),
    )
