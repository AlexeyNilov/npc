import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

from npc.experiments.wolf_affect import (
    AFFECT_SENSOR_PROMPT,
    CandidateAffect,
    decide_action,
    load_corpus,
    parse_candidate,
    run_case,
)


def candidate(affect: str, evidence: str) -> str:
    return json.dumps({"affect": affect, "evidence": evidence})


def completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def test_accepted_grounded_hostile_candidate_attacks() -> None:
    result = asyncio.run(
        run_case(
            "Get out of my way, or I will hurt you.",
            completion(candidate("hostile", "I will hurt you")),
        )
    )

    assert result.candidate == CandidateAffect("hostile", "I will hurt you")
    assert result.validation_result == "accepted"
    assert result.action == "attack"


def test_accepted_non_hostile_and_unclear_candidates_do_nothing() -> None:
    non_hostile = asyncio.run(run_case("I mean no harm.", completion(candidate("non_hostile", "no harm"))))
    unclear = asyncio.run(run_case("I am not sure.", completion(candidate("unclear", "not sure"))))

    assert non_hostile.validation_result == "accepted"
    assert non_hostile.action == "do_nothing"
    assert unclear.validation_result == "accepted"
    assert unclear.action == "do_nothing"


def test_rejected_candidates_cannot_cause_an_attack() -> None:
    cases = (
        ("not json", "invalid_candidate"),
        (candidate("friendly", "I will hurt you"), "unsupported_affect"),
        (candidate("hostile", ""), "evidence_empty"),
        (candidate("hostile", "I own this forest"), "evidence_not_in_player_message"),
    )

    for raw_candidate, validation_result in cases:
        result = asyncio.run(run_case("I will hurt you.", completion(raw_candidate)))
        assert result.validation_result == validation_result
        assert result.action == "do_nothing"


def test_parser_rejects_key_set_and_type_violations() -> None:
    assert parse_candidate('{"affect": "hostile"}') is None
    assert parse_candidate('{"affect": "hostile", "evidence": ["threat"]}') is None
    assert parse_candidate('{"affect": "hostile", "evidence": "threat", "extra": true}') is None


def test_json_fenced_candidate_is_parsed_and_can_reach_the_policy() -> None:
    raw_candidate = '```json\n{"affect": "hostile", "evidence": "I will hurt you"}\n```'

    result = asyncio.run(run_case("I will hurt you.", completion(raw_candidate)))

    assert result.candidate == CandidateAffect("hostile", "I will hurt you")
    assert result.validation_result == "accepted"
    assert result.action == "attack"


def test_policy_is_deterministic_from_an_accepted_perception() -> None:
    perception = CandidateAffect("hostile", "I will hurt you")

    assert decide_action(perception.affect) == "attack"
    assert decide_action(perception.affect) == "attack"
    assert decide_action(None) == "do_nothing"


def test_checked_in_corpus_has_required_cases_and_expected_trace_fields() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "wolf_affect.yaml"
    cases = load_corpus(corpus_path)
    expected_by_id = {case["id"]: case for case in cases}

    assert set(expected_by_id) == {"hostile-threat", "calm-greeting", "fearful-plea", "ambiguous-statement"}
    assert {case["expected_affect"] for case in cases} == {"hostile", "non_hostile", "unclear"}
    assert {case["expected_action"] for case in cases} == {"attack", "do_nothing"}

    for case in cases:
        raw_candidate = candidate(case["expected_affect"], _evidence_for(case["id"]))
        trace = asyncio.run(run_case(case["player_message"], completion(raw_candidate), case))

        assert trace.raw_candidate == raw_candidate
        assert trace.candidate is not None
        assert trace.validation_result == "accepted"
        assert trace.expected_affect == case["expected_affect"]
        assert trace.expected_action == case["expected_action"]
        assert trace.action == case["expected_action"]


def test_sensor_prompt_limits_the_model_to_affect_and_player_text_evidence() -> None:
    assert "exactly `affect` and `evidence`" in AFFECT_SENSOR_PROMPT
    assert "world" not in AFFECT_SENSOR_PROMPT.lower()
    assert "action" not in AFFECT_SENSOR_PROMPT.lower()


def _evidence_for(case_id: str) -> str:
    return {
        "hostile-threat": "I will hurt you",
        "calm-greeting": "I mean no harm",
        "fearful-plea": "I am scared",
        "ambiguous-statement": "not sure what to do",
    }[case_id]
