import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import cast

from npc.experiments.wolf_threat import (
    THREAT_SENSOR_PROMPT,
    CandidateThreat,
    decide_action,
    load_corpus,
    run_case,
)


def candidate(threat: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({"threat": threat, "certainty": certainty, "evidence": evidence})


def completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def test_accepted_grounded_true_candidate_attacks() -> None:
    result = asyncio.run(
        run_case(
            "Get out of my way, or I will hurt you.",
            completion(candidate(True, 0.7, "I will hurt you")),
        )
    )

    assert result.candidate == CandidateThreat(True, 0.7, "I will hurt you")
    assert result.validation_result == "accepted"
    assert result.action == "attack"


def test_wolf_trace_names_its_target_and_wrapper_makes_one_completion_call() -> None:
    calls = 0

    async def one_response(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return candidate(False, 0.5, None)

    result = asyncio.run(run_case("Hello wolf.", one_response))

    assert calls == 1
    assert result.target == "wolf"


def test_accepted_false_candidate_does_nothing() -> None:
    result = asyncio.run(run_case("Hello there.", completion(candidate(False, 0.3, None))))

    assert result.candidate == CandidateThreat(False, 0.3, None)
    assert result.validation_result == "accepted"
    assert result.action == "do_nothing"


def test_malformed_shapes_and_types_cannot_cause_an_attack() -> None:
    raw_candidates = (
        "not json",
        '{"threat": true, "certainty": 0.7}',
        '{"threat": "true", "certainty": 0.7, "evidence": "hurt you"}',
        '{"threat": true, "certainty": true, "evidence": "hurt you"}',
        '{"threat": false, "certainty": 0.7, "evidence": "hurt you"}',
        '{"threat": false, "certainty": 0.7, "evidence": null, "extra": true}',
    )

    for raw_candidate in raw_candidates:
        result = asyncio.run(run_case("I will hurt you.", completion(raw_candidate)))
        assert result.validation_result == "invalid_candidate"
        assert result.action == "do_nothing"


def test_empty_or_ungrounded_true_evidence_cannot_cause_an_attack() -> None:
    empty = asyncio.run(run_case("I will hurt you.", completion(candidate(True, 0.8, ""))))
    ungrounded = asyncio.run(run_case("I will hurt you.", completion(candidate(True, 0.8, "I own this forest"))))

    assert empty.validation_result == "evidence_empty"
    assert empty.action == "do_nothing"
    assert ungrounded.validation_result == "evidence_not_in_player_message"
    assert ungrounded.action == "do_nothing"


def test_out_of_range_or_non_finite_certainty_cannot_cause_an_attack() -> None:
    cases = (
        (candidate(True, -0.1, "hurt you"), "certainty_out_of_range"),
        (candidate(True, 1.1, "hurt you"), "certainty_out_of_range"),
        ('{"threat": true, "certainty": NaN, "evidence": "hurt you"}', "certainty_not_finite"),
    )

    for raw_candidate, validation_result in cases:
        result = asyncio.run(run_case("I will hurt you.", completion(raw_candidate)))
        assert result.validation_result == validation_result
        assert result.action == "do_nothing"


def test_arbitrarily_large_integer_certainty_cannot_cause_an_attack() -> None:
    raw_candidate = '{"threat": true, "certainty": ' + "9" * 400 + ', "evidence": "hurt you"}'

    result = asyncio.run(run_case("I will hurt you.", completion(raw_candidate)))

    assert result.validation_result == "certainty_out_of_range"
    assert result.action == "do_nothing"


def test_policy_is_deterministic_and_certainty_invariant() -> None:
    low_certainty = asyncio.run(run_case("I will hurt you.", completion(candidate(True, 0.01, "hurt you"))))
    high_certainty = asyncio.run(run_case("I will hurt you.", completion(candidate(True, 0.99, "hurt you"))))

    assert decide_action(True) == "attack"
    assert decide_action(False) == "do_nothing"
    assert low_certainty.action == high_certainty.action == "attack"


def test_checked_in_corpus_has_required_cases_expected_fields_and_one_call_per_case() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "wolf_threat.yaml"
    cases = load_corpus(corpus_path)
    expected_by_id = {case["id"]: case for case in cases}

    assert set(expected_by_id) == {"direct-threat", "calm-greeting", "fearful-plea", "ambiguous-statement"}
    assert {case["expected_threat"] for case in cases} == {True, False}
    assert {case["expected_action"] for case in cases} == {"attack", "do_nothing"}

    for case in cases:
        calls = 0

        async def one_response(_: str, __: str) -> str:
            nonlocal calls
            calls += 1
            return candidate(cast(bool, case["expected_threat"]), 0.5, _evidence_for(case))

        trace = asyncio.run(run_case(cast(str, case["player_message"]), one_response, case))

        assert calls == 1
        assert trace.expected_threat == case["expected_threat"]
        assert trace.expected_action == case["expected_action"]
        assert trace.action == case["expected_action"]


def test_sensor_prompt_limits_the_model_to_one_binary_player_text_question() -> None:
    assert "exactly `threat`, `certainty`, and `evidence`" in THREAT_SENSOR_PROMPT
    assert "credible hostile threat toward the wolf" in THREAT_SENSOR_PROMPT
    assert "world" not in THREAT_SENSOR_PROMPT.lower()
    assert "action" not in THREAT_SENSOR_PROMPT.lower()


def _evidence_for(case: dict[str, object]) -> str | None:
    return {
        "direct-threat": "I will hurt you",
        "calm-greeting": None,
        "fearful-plea": None,
        "ambiguous-statement": None,
    }[str(case["id"])]
