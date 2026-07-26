import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path
from typing import cast

from npc.experiments.fox_distance_feedback import (
    APPROACH_DISPLACEMENT,
    FLEE_DISPLACEMENT,
    HEARING_RANGE,
    MINIMUM_DISTANCE,
    load_corpus,
    run_fixture,
    run_turn,
)


def candidate(key: str, value: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({key: value, "certainty": certainty, "evidence": evidence})


def test_audible_turn_calls_independent_sensors_and_threat_has_priority() -> None:
    prompts: list[str] = []

    async def complete(_: str, prompt: str) -> str:
        prompts.append(prompt)
        if "hostile threat" in prompt:
            return candidate("threat", True, 0.8, "I will hurt you")
        return candidate("food_offer", True, 0.8, "I offer you this fresh meat")

    trace = asyncio.run(run_turn("Fox, I will hurt you, but I offer you this fresh meat.", HEARING_RANGE, complete))

    assert len(prompts) == 2
    assert "hostile threat" in prompts[0]
    assert "explicitly offer food" in prompts[1]
    assert trace.threat_sensor_called is trace.food_offer_sensor_called is True
    assert trace.threat_validation_result == trace.food_offer_validation_result == "accepted"
    assert trace.choice == trace.executed_action == "flee"
    assert trace.resulting_distance == HEARING_RANGE + FLEE_DISPLACEMENT


def test_accepted_food_offer_approaches_and_feedback_carries_forward_with_minimum_distance() -> None:
    async def complete(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return candidate("threat", False, 0.5, None)
        return candidate("food_offer", True, 0.5, "I offer you this fresh meat")

    first = asyncio.run(run_turn("Fox, I offer you this fresh meat.", 4, complete))
    second = asyncio.run(run_turn("Fox, I offer you this fresh meat.", first.feedback_distance, complete))

    assert first.choice == first.executed_action == "approach"
    assert first.resulting_distance == first.feedback_distance == 4 - APPROACH_DISPLACEMENT
    assert second.starting_distance == 1
    assert second.resulting_distance == second.feedback_distance == MINIMUM_DISTANCE


def test_rejected_sensor_cannot_cause_its_action_or_suppress_other_sensor() -> None:
    async def rejected_threat(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return "not json"
        return candidate("food_offer", True, 0.8, "I offer you this fresh meat")

    async def rejected_offer(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return candidate("threat", False, 0.8, None)
        return candidate("food_offer", True, 0.8, "")

    offer = asyncio.run(run_turn("Fox, I offer you this fresh meat.", 10, rejected_threat))
    rejected = asyncio.run(run_turn("Fox, I offer you this fresh meat.", 10, rejected_offer))

    assert offer.threat_validation_result == "invalid_candidate"
    assert offer.choice == "approach"
    assert offer.resulting_distance == 7
    assert rejected.food_offer_validation_result == "evidence_empty"
    assert rejected.choice == "do_nothing"
    assert rejected.resulting_distance == 10


def test_malformed_invalid_certainty_empty_and_ungrounded_candidates_from_either_sensor_fail_closed() -> None:
    threat_message = "Fox, I will hurt you."
    offer_message = "Fox, I offer you this fresh meat."
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
        trace = asyncio.run(
            run_turn(threat_message, 10, _sensor_completion(raw_candidate, candidate("food_offer", False, 0.7, None)))
        )
        assert trace.threat_validation_result != "accepted"
        assert trace.choice == "do_nothing"

    for raw_candidate in rejected_offers:
        trace = asyncio.run(
            run_turn(offer_message, 10, _sensor_completion(candidate("threat", False, 0.7, None), raw_candidate))
        )
        assert trace.food_offer_validation_result != "accepted"
        assert trace.choice == "do_nothing"


def test_initially_out_of_range_turn_skips_both_sensors_and_preserves_distance() -> None:
    calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return "not used"

    trace = asyncio.run(run_turn("Fox, I offer you this fresh meat.", 11, complete))

    assert calls == 0
    assert trace.heard is False
    assert trace.threat_sensor_called is trace.food_offer_sensor_called is False
    assert (
        trace.threat_raw_candidate
        is trace.threat_candidate
        is trace.threat_validation_result
        is trace.food_offer_raw_candidate
        is trace.food_offer_candidate
        is trace.food_offer_validation_result
        is None
    )
    assert trace.choice == trace.executed_action == "do_nothing"
    assert trace.resulting_distance == trace.feedback_distance == 11


def test_turn_trace_and_checked_in_corpus_cover_all_fox_actions() -> None:
    trace = asyncio.run(run_turn("Fox, hello.", 10, _completion(False, False)))
    assert set(asdict(trace)) == {
        "player_message",
        "starting_distance",
        "heard",
        "threat_sensor_called",
        "threat_raw_candidate",
        "threat_candidate",
        "threat_validation_result",
        "food_offer_sensor_called",
        "food_offer_raw_candidate",
        "food_offer_candidate",
        "food_offer_validation_result",
        "choice",
        "executed_action",
        "resulting_distance",
        "feedback_distance",
    }
    json.dumps(asdict(trace), sort_keys=True)

    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_distance_feedback.yaml"
    cases = {cast(str, case["id"]): case for case in load_corpus(corpus_path)}
    assert set(cases) == {"threat-feedback", "offer-feedback", "rejected-offer", "out-of-range-offer"}

    traces = {case_id: asyncio.run(run_fixture(case)) for case_id, case in cases.items()}
    assert [trace.resulting_distance for trace in traces["threat-feedback"]] == [15, 15]
    assert [trace.resulting_distance for trace in traces["offer-feedback"]] == [7, 4, 1]
    assert traces["rejected-offer"][0].executed_action == "do_nothing"
    assert traces["out-of-range-offer"][0].threat_sensor_called is False

    for case_id, case in cases.items():
        for turn, fixture_trace in zip(cast(list[dict[str, object]], case["turns"]), traces[case_id], strict=True):
            assert fixture_trace.executed_action == turn["expected_action"]
            assert fixture_trace.resulting_distance == turn["expected_resulting_distance"]


def _completion(threat: bool, food_offer: bool) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return candidate("threat", threat, 0.5, "I will hurt you" if threat else None)
        return candidate("food_offer", food_offer, 0.5, "I offer you this fresh meat" if food_offer else None)

    return complete


def _sensor_completion(threat_response: str, food_offer_response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, prompt: str) -> str:
        return threat_response if "hostile threat" in prompt else food_offer_response

    return complete
