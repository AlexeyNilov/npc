import asyncio
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from npc.experiments.fox_hunter_shared_world import (
    FOX_DESCRIPTION,
    HUNTER_DESCRIPTION,
    CanonicalState,
    load_corpus,
    replay,
    run_fixture,
    run_turn,
)


def response(percept: str, description: object, answers: tuple[bool, bool]) -> str:
    questions = description.questions  # type: ignore[attr-defined]
    return json.dumps(
        {
            "percept": percept,
            "answers": [
                {"question": questions[0], "answer": answers[0], "evidence": percept},
                {"question": questions[1], "answer": answers[1], "evidence": percept},
            ],
        }
    )


def test_ready_materials_records_separate_observations_proposals_and_hunter_first_capture() -> None:
    calls: dict[str, tuple[str, str, tuple[str, ...]]] = {}

    async def fox(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["fox"] = (accessible, profile, questions)
        return response("The clearing seems quiet and the food seems reachable.", FOX_DESCRIPTION, (False, True))

    async def hunter(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["hunter"] = (accessible, profile, questions)
        return response(
            "Fresh tracks suggest the fox may approach and my materials are ready.", HUNTER_DESCRIPTION, (True, True)
        )

    trace = asyncio.run(run_turn(fox, hunter))

    assert calls == {
        "fox": (
            "You are at the edge of a clearing. You smell food in the clearing. The clearing appears quiet.",
            FOX_DESCRIPTION.epistemic_profile,
            FOX_DESCRIPTION.questions,
        ),
        "hunter": (
            "You are concealed beside a clearing. Fresh fox tracks lead toward food. Your trap materials are ready.",
            HUNTER_DESCRIPTION.epistemic_profile,
            HUNTER_DESCRIPTION.questions,
        ),
    }
    assert trace.fox.proposal == "approach_food"
    assert trace.hunter.proposal == "set_trap"
    assert trace.resolution_order == ("hunter", "fox")
    assert trace.decisions == ("set_trap", "fox_caught_by_trap")
    assert trace.resulting_canonical_state.trap_set is True
    assert trace.resulting_canonical_state.fox_caught is True
    assert trace.resulting_canonical_state.food_consumed is False
    assert trace.outcome == "fox_caught_by_trap"
    assert trace.feedback == {
        "fox": "A hidden trap catches you as you reach the food.",
        "hunter": "Your trap catches the fox.",
    }


def test_unavailable_materials_source_variation_changes_hunter_observation_and_outcome() -> None:
    calls: dict[str, tuple[str, str, tuple[str, ...]]] = {}

    async def fox(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["fox"] = (accessible, profile, questions)
        return response("The clearing seems quiet and the food seems reachable.", FOX_DESCRIPTION, (False, True))

    async def hunter(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["hunter"] = (accessible, profile, questions)
        return response("Fresh tracks suggest an approach, but materials are not ready.", HUNTER_DESCRIPTION, (True, False))

    trace = asyncio.run(run_turn(fox, hunter, CanonicalState(trap_materials_ready=False)))

    assert calls["fox"][0] == "You are at the edge of a clearing. You smell food in the clearing. The clearing appears quiet."
    assert calls["hunter"][0] == (
        "You are concealed beside a clearing. Fresh fox tracks lead toward food. Your trap materials are not ready."
    )
    assert trace.hunter.proposal == "wait"
    assert trace.outcome == "fox_reaches_food"
    assert trace.resulting_canonical_state.fox_location == "food"
    assert trace.resulting_canonical_state.food_consumed is True
    assert trace.feedback == {"fox": "You reach the food.", "hunter": "The fox reaches the food."}


def test_mediation_boundaries_are_actor_local_and_invalid_responses_fail_closed() -> None:
    calls: dict[str, tuple[str, str, tuple[str, ...]]] = {}

    async def fox(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["fox"] = (accessible, profile, questions)
        return "not json"

    async def hunter(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls["hunter"] = (accessible, profile, questions)
        return response("Tracks indicate an approach and materials are ready.", HUNTER_DESCRIPTION, (True, True))

    trace = asyncio.run(run_turn(fox, hunter))

    assert all(word not in calls["fox"][0].lower() for word in ("hunter", "track", "trap", "material"))
    assert "edge" not in calls["hunter"][0].lower()
    assert FOX_DESCRIPTION.questions[0] not in calls["hunter"][2]
    assert trace.fox.proposal == "wait"
    assert trace.hunter.proposal == "set_trap"
    assert trace.resulting_canonical_state.trap_set is True
    assert trace.outcome == "waited"


@pytest.mark.parametrize("invalid_actor", ("fox", "hunter"))
def test_missing_evidence_fails_closed_only_for_the_invalid_actor(invalid_actor: str) -> None:
    async def fox(_: str, __: str, ___: tuple[str, ...]) -> str:
        if invalid_actor == "fox":
            return response("The clearing seems quiet.", FOX_DESCRIPTION, (False, True)).replace(
                '"evidence": "The clearing seems quiet."', '"evidence": "missing"'
            )
        return response("The clearing seems quiet and food seems reachable.", FOX_DESCRIPTION, (False, True))

    async def hunter(_: str, __: str, ___: tuple[str, ...]) -> str:
        if invalid_actor == "hunter":
            return response("Tracks suggest an approach and materials are ready.", HUNTER_DESCRIPTION, (True, True)).replace(
                '"evidence": "Tracks suggest an approach and materials are ready."', '"evidence": "missing"'
            )
        return response("Tracks suggest an approach and materials are ready.", HUNTER_DESCRIPTION, (True, True))

    trace = asyncio.run(run_turn(fox, hunter))

    if invalid_actor == "fox":
        assert trace.fox.proposal == "wait"
        assert trace.hunter.proposal == "set_trap"
        assert trace.outcome == "waited"
    else:
        assert trace.fox.proposal == "approach_food"
        assert trace.hunter.proposal == "wait"
        assert trace.outcome == "fox_reaches_food"


def test_fixture_trace_is_json_safe_and_replay_rejects_changed_authority() -> None:
    case = load_corpus(Path(__file__).parents[1] / "scenarios" / "fox_hunter_shared_world.yaml")[0]
    trace = asyncio.run(run_fixture(case))[0]

    json.dumps(asdict(trace), sort_keys=True)
    assert replay(trace) == trace
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, resolution_order=("fox", "hunter")))
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, decisions=("wait", "fox_caught_by_trap")))
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, transitions=("changed",)))
    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, feedback={"fox": "changed", "hunter": "changed"}))
