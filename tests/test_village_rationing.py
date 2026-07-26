import asyncio
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from npc.experiments.village_rationing import (
    HOUSEHOLD_ONE_DESCRIPTION,
    HOUSEHOLD_TWO_DESCRIPTION,
    ORGANISATION_DESCRIPTION,
    CanonicalState,
    load_corpus,
    replay,
    run_fixture,
    run_turn,
)


def response(percept: str, description: object, answers: tuple[bool, bool], proposal: object) -> str:
    questions = description.questions  # type: ignore[attr-defined]
    return json.dumps(
        {
            "percept": percept,
            "answers": [
                {"question": questions[0], "answer": answers[0], "evidence": percept},
                {"question": questions[1], "answer": answers[1], "evidence": percept},
            ],
            "proposal": proposal,
        }
    )


def valid_household_response(description: object) -> str:
    return response(
        "Our household needs this emergency food and can submit the fixed claim.", description, (True, True), "claim_4"
    )


def valid_organisation_response(allocation: dict[str, int]) -> str:
    return response(
        "The public ledger and available reserve support this priority allocation.",
        ORGANISATION_DESCRIPTION,
        (True, True),
        allocation,
    )


def test_six_unit_turn_separates_private_inputs_and_commits_priority_allocation() -> None:
    calls: dict[str, tuple[str, str, tuple[str, ...]]] = {}

    async def household_one(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["household_one"] = (accessible, profile, questions)
        return valid_household_response(HOUSEHOLD_ONE_DESCRIPTION)

    async def household_two(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["household_two"] = (accessible, profile, questions)
        return valid_household_response(HOUSEHOLD_TWO_DESCRIPTION)

    async def organisation(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["organisation"] = (accessible, profile, questions)
        return valid_organisation_response({"household_one": 4, "household_two": 2})

    trace = asyncio.run(run_turn(household_one, household_two, organisation))

    assert calls["household_one"] == (
        "Your household has no food for today; your two dependants need emergency rations.",
        HOUSEHOLD_ONE_DESCRIPTION.epistemic_profile,
        HOUSEHOLD_ONE_DESCRIPTION.questions,
    )
    assert calls["household_two"] == (
        "Your household has no food for today; your infant needs emergency rations.",
        HOUSEHOLD_TWO_DESCRIPTION.epistemic_profile,
        HOUSEHOLD_TWO_DESCRIPTION.questions,
    )
    expected_organisation_observation = (
        "Emergency food reserve: 6 units. Public claim ledger: household_one requests 4 at priority tier 1; "
        "household_two requests 4 at priority tier 2."
    )
    assert calls["organisation"] == (
        expected_organisation_observation,
        ORGANISATION_DESCRIPTION.epistemic_profile,
        ORGANISATION_DESCRIPTION.questions,
    )
    household_one_private = "two dependants"
    household_two_private = "infant"
    assert household_two_private not in calls["household_one"][0]
    assert household_one_private not in calls["household_two"][0]
    assert all(
        fact not in calls["organisation"][0] for fact in (household_one_private, household_two_private, "no food for today")
    )
    assert HOUSEHOLD_TWO_DESCRIPTION.epistemic_profile not in calls["household_one"][1]
    assert HOUSEHOLD_ONE_DESCRIPTION.epistemic_profile not in calls["household_two"][1]
    assert HOUSEHOLD_ONE_DESCRIPTION.questions != ORGANISATION_DESCRIPTION.questions
    assert HOUSEHOLD_TWO_DESCRIPTION.questions != ORGANISATION_DESCRIPTION.questions
    assert trace.claim_ledger == (("household_one", 4, 1), ("household_two", 4, 2))
    assert trace.allocation_proposal == (4, 2)
    assert trace.validation_decision == "accepted"
    assert trace.resulting_canonical_state.reserve_units == 0
    assert trace.resulting_canonical_state.committed_allocations == (("household_one", 4), ("household_two", 2))
    assert trace.feedback == {
        "household_one": "Your household receives 4 emergency-food units.",
        "household_two": "Your household receives 2 emergency-food units.",
        "organisation": "The priority allocation was accepted.",
    }
    for feedback in trace.feedback.values():
        assert household_one_private not in feedback
        assert household_two_private not in feedback


def test_changing_only_reserve_changes_organisation_observation_and_authoritative_result() -> None:
    calls: dict[str, str] = {}

    async def household_one(accessible: str, _: str, __: tuple[str, ...]) -> str:
        calls["household_one"] = accessible
        return valid_household_response(HOUSEHOLD_ONE_DESCRIPTION)

    async def household_two(accessible: str, _: str, __: tuple[str, ...]) -> str:
        calls["household_two"] = accessible
        return valid_household_response(HOUSEHOLD_TWO_DESCRIPTION)

    async def organisation(accessible: str, _: str, __: tuple[str, ...]) -> str:
        calls["organisation"] = accessible
        return valid_organisation_response({"household_one": 4, "household_two": 0})

    trace = asyncio.run(run_turn(household_one, household_two, organisation, CanonicalState(reserve_units=4)))

    assert calls["household_one"] == "Your household has no food for today; your two dependants need emergency rations."
    assert calls["household_two"] == "Your household has no food for today; your infant needs emergency rations."
    assert calls["organisation"].startswith("Emergency food reserve: 4 units.")
    assert trace.resulting_canonical_state.reserve_units == 0
    assert trace.resulting_canonical_state.committed_allocations == (("household_one", 4), ("household_two", 0))
    assert trace.validation_decision == "accepted"


def test_invalid_allocation_is_rejected_without_canonical_change() -> None:
    async def household_one(_: str, __: str, ___: tuple[str, ...]) -> str:
        return valid_household_response(HOUSEHOLD_ONE_DESCRIPTION)

    async def household_two(_: str, __: str, ___: tuple[str, ...]) -> str:
        return valid_household_response(HOUSEHOLD_TWO_DESCRIPTION)

    async def organisation(_: str, __: str, ___: tuple[str, ...]) -> str:
        return valid_organisation_response({"household_one": 4, "household_two": 4})

    trace = asyncio.run(run_turn(household_one, household_two, organisation))

    assert trace.validation_decision == "rejected"
    assert trace.transitions == ()
    assert trace.resulting_canonical_state == CanonicalState()
    assert trace.feedback["organisation"] == "The allocation proposal was rejected."


@pytest.mark.parametrize("invalid_actor", ("household_one", "household_two", "organisation"))
@pytest.mark.parametrize("invalid_response", ("not json", '{"percept":"missing fields"}', 3))
def test_malformed_or_unsupported_mediation_fails_closed_for_every_actor(invalid_actor: str, invalid_response: object) -> None:
    async def household_one(_: str, __: str, ___: tuple[str, ...]) -> object:
        return invalid_response if invalid_actor == "household_one" else valid_household_response(HOUSEHOLD_ONE_DESCRIPTION)

    async def household_two(_: str, __: str, ___: tuple[str, ...]) -> object:
        return invalid_response if invalid_actor == "household_two" else valid_household_response(HOUSEHOLD_TWO_DESCRIPTION)

    async def organisation(_: str, __: str, ___: tuple[str, ...]) -> object:
        if invalid_actor == "organisation":
            return invalid_response
        return valid_organisation_response({"household_one": 4, "household_two": 2})

    trace = asyncio.run(run_turn(household_one, household_two, organisation))  # type: ignore[arg-type]

    assert trace.resulting_canonical_state == CanonicalState()
    assert trace.validation_decision == "rejected"


@pytest.mark.parametrize("invalid_actor", ("household_one", "household_two", "organisation"))
def test_unsupported_proposal_fails_closed_for_every_actor(invalid_actor: str) -> None:
    async def household_one(_: str, __: str, ___: tuple[str, ...]) -> str:
        proposal: object = "unsupported" if invalid_actor == "household_one" else "claim_4"
        return response(
            "Our household needs this emergency food and can submit the fixed claim.",
            HOUSEHOLD_ONE_DESCRIPTION,
            (True, True),
            proposal,
        )

    async def household_two(_: str, __: str, ___: tuple[str, ...]) -> str:
        proposal: object = "unsupported" if invalid_actor == "household_two" else "claim_4"
        return response(
            "Our household needs this emergency food and can submit the fixed claim.",
            HOUSEHOLD_TWO_DESCRIPTION,
            (True, True),
            proposal,
        )

    async def organisation(_: str, __: str, ___: tuple[str, ...]) -> str:
        proposal: object = "unsupported" if invalid_actor == "organisation" else {"household_one": 4, "household_two": 2}
        return response(
            "The public ledger and available reserve support this priority allocation.",
            ORGANISATION_DESCRIPTION,
            (True, True),
            proposal,
        )

    trace = asyncio.run(run_turn(household_one, household_two, organisation))

    assert trace.resulting_canonical_state == CanonicalState()
    assert trace.validation_decision == "rejected"


def test_fixture_trace_is_json_safe_and_replays_without_mediation() -> None:
    case = load_corpus(Path(__file__).parents[1] / "scenarios" / "village_rationing.yaml")[0]
    trace = asyncio.run(run_fixture(case))[0]

    json.dumps(asdict(trace), sort_keys=True)
    assert replay(trace) == trace
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, allocation_proposal=(4, 4)))
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, feedback={**trace.feedback, "organisation": "changed"}))
