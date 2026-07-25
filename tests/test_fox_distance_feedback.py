import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path
from typing import cast

from npc.experiments.fox_distance_feedback import (
    FLEE_DISPLACEMENT,
    HEARING_RANGE,
    load_corpus,
    run_fixture,
    run_turn,
)


def candidate(threat: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({"threat": threat, "certainty": certainty, "evidence": evidence})


def test_hearing_boundary_is_audible_and_accepted_threat_flees() -> None:
    calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return candidate(True, 0.8, "I will hurt you")

    trace = asyncio.run(run_turn("Fox, I will hurt you.", HEARING_RANGE, complete))

    assert calls == 1
    assert trace.heard is True
    assert trace.sensor_called is True
    assert trace.validation_result == "accepted"
    assert trace.choice == trace.executed_action == "flee"
    assert trace.resulting_distance == HEARING_RANGE + FLEE_DISPLACEMENT
    assert trace.feedback_distance == trace.resulting_distance


def test_two_turn_flee_feedback_skips_repeated_threat_before_sensor() -> None:
    calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return candidate(True, 0.8, "I will hurt you")

    first = asyncio.run(run_turn("Fox, I will hurt you.", 10, complete))
    second = asyncio.run(run_turn("Fox, I will hurt you.", first.feedback_distance, complete))

    assert calls == 1
    assert first.resulting_distance == first.feedback_distance == 15
    assert second.starting_distance == 15
    assert second.heard is False
    assert second.sensor_called is False
    assert second.raw_candidate is second.candidate is second.validation_result is None
    assert second.choice == second.executed_action == "do_nothing"
    assert second.resulting_distance == second.feedback_distance == 15


def test_audible_rejected_candidates_do_nothing_without_movement() -> None:
    message = "Fox, I will hurt you."
    responses = {
        "malformed": "not json",
        "invalid-certainty": candidate(True, 1.1, "I will hurt you"),
        "empty-evidence": candidate(True, 0.8, ""),
        "ungrounded": candidate(True, 0.8, "I own this forest"),
    }

    for validation_result, response in responses.items():
        calls = 0

        async def complete(_: str, __: str, response: str = response) -> str:
            nonlocal calls
            calls += 1
            return response

        trace = asyncio.run(run_turn(message, 10, complete))

        assert calls == 1
        assert trace.heard is True
        assert trace.sensor_called is True
        assert (
            trace.validation_result
            == {
                "malformed": "invalid_candidate",
                "invalid-certainty": "certainty_out_of_range",
                "empty-evidence": "evidence_empty",
                "ungrounded": "evidence_not_in_player_message",
            }[validation_result]
        )
        assert trace.choice == trace.executed_action == "do_nothing"
        assert trace.resulting_distance == trace.feedback_distance == 10


def test_initially_out_of_range_turn_has_no_candidate_or_movement() -> None:
    calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return candidate(True, 0.8, "I will hurt you")

    trace = asyncio.run(run_turn("Fox, I will hurt you.", 11, complete))

    assert calls == 0
    assert trace.heard is trace.sensor_called is False
    assert trace.raw_candidate is trace.candidate is trace.validation_result is None
    assert trace.choice == trace.executed_action == "do_nothing"
    assert trace.resulting_distance == trace.feedback_distance == 11


def test_turn_trace_is_complete_and_json_safe() -> None:
    trace = asyncio.run(run_turn("Fox, hello.", 10, _completion(candidate(False, 0.5, None))))

    assert set(asdict(trace)) == {
        "player_message",
        "starting_distance",
        "heard",
        "sensor_called",
        "raw_candidate",
        "candidate",
        "validation_result",
        "choice",
        "executed_action",
        "resulting_distance",
        "feedback_distance",
    }
    json.dumps(asdict(trace), sort_keys=True)


def test_checked_in_corpus_has_required_fixture_expectations() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_distance_feedback.yaml"
    cases = {cast(str, case["id"]): case for case in load_corpus(corpus_path)}

    assert set(cases) == {"direct-threat-feedback", "rejected-true-candidate", "out-of-range-threat"}
    traces = {case_id: asyncio.run(run_fixture(case)) for case_id, case in cases.items()}
    direct = traces["direct-threat-feedback"]
    rejected = traces["rejected-true-candidate"][0]
    out_of_range = traces["out-of-range-threat"][0]

    assert [trace.sensor_called for trace in direct] == [True, False]
    assert [trace.resulting_distance for trace in direct] == [15, 15]
    assert rejected.sensor_called is True
    assert rejected.executed_action == "do_nothing"
    assert rejected.resulting_distance == 10
    assert out_of_range.sensor_called is False
    assert out_of_range.resulting_distance == 11

    for case_id, case in cases.items():
        for turn, trace in zip(cast(list[dict[str, object]], case["turns"]), traces[case_id], strict=True):
            assert trace.executed_action == turn["expected_action"]
            assert trace.resulting_distance == turn["expected_resulting_distance"]


def _completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete
