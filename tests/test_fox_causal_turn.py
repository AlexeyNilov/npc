import asyncio
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from npc.experiments.fox_causal_turn import (
    EPISTEMIC_PROFILE,
    QUESTIONS,
    CanonicalState,
    load_corpus,
    replay,
    resolve_proposal,
    run_fixture,
    run_turn,
)


def mediation(percept: str, threat: bool, reachable: bool, *, evidence: str | None = None) -> str:
    return json.dumps(
        {
            "percept": percept,
            "answers": [
                {"question": QUESTIONS[0], "answer": threat, "evidence": evidence or percept},
                {"question": QUESTIONS[1], "answer": reachable, "evidence": evidence or percept},
            ],
        }
    )


def test_actor_can_mention_blocked_while_canonical_path_stays_withheld_until_resolution() -> None:
    calls: list[tuple[str, str, tuple[str, ...]]] = []

    async def complete(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls.append((accessible, profile, questions))
        return mediation(
            "The clearing seems quiet; the food may be blocked, but it seems reachable.", False, True, evidence="seems"
        )

    trace = asyncio.run(run_turn(complete))

    assert calls == [("You are in a clearing. You smell food nearby. You hear leaves rustling.", EPISTEMIC_PROFILE, QUESTIONS)]
    assert "blocked" not in repr(calls[0]).lower()
    assert trace.subjective_percept is not None
    assert "blocked" in trace.subjective_percept
    assert trace.proposal == "approach_food"
    assert trace.resolution == "food_path_blocked"
    assert (
        trace.initial_canonical_state
        == trace.resulting_canonical_state
        == CanonicalState(
            location="clearing",
            food_scent_nearby=True,
            leaves_rustling=True,
            food_path_blocked=True,
        )
    )
    assert trace.feedback == "The path to the food is blocked."
    assert [answer.question for answer in trace.answers] == list(QUESTIONS)
    assert all(answer.evidence in trace.subjective_percept for answer in trace.answers)


def test_false_belief_stays_actor_local_and_replay_does_not_call_mediation() -> None:
    async def complete(_: str, __: str, ___: tuple[str, ...]) -> str:
        return mediation("I can probably reach the food.", False, True, evidence="reach the food")

    trace = asyncio.run(run_turn(complete))
    replayed = replay(trace)

    assert trace.answers[1].answer is True
    assert trace.initial_canonical_state.food_path_blocked is True
    assert replayed == trace


@pytest.mark.parametrize(
    "response",
    [
        "not json",
        json.dumps({"percept": "", "answers": []}),
        json.dumps(
            {
                "percept": "Food seems close.",
                "answers": [
                    {"question": QUESTIONS[0], "answer": False, "evidence": "Food"},
                    {"question": QUESTIONS[1], "answer": True, "evidence": "missing"},
                ],
            }
        ),
    ],
)
def test_malformed_or_rejected_mediation_fails_closed_without_an_unauthorized_transition(response: str) -> None:
    async def complete(_: str, __: str, ___: tuple[str, ...]) -> str:
        return response

    trace = asyncio.run(run_turn(complete))

    assert trace.proposal == "wait"
    assert trace.resolution == "waited"
    assert trace.resulting_canonical_state == trace.initial_canonical_state
    assert trace.feedback == "The fox waited."


def test_only_core_resolution_commits_and_unsupported_proposals_fail_closed() -> None:
    initial = CanonicalState(
        location="clearing",
        food_scent_nearby=True,
        leaves_rustling=True,
        food_path_blocked=True,
    )

    resolution, resulting, feedback = resolve_proposal(initial, "not_an_action")

    assert (resolution, resulting, feedback) == ("waited", initial, "The fox waited.")
    assert resolve_proposal(initial, "approach_food")[0] == "food_path_blocked"


@pytest.mark.parametrize(
    ("canonical_state", "expected_accessible"),
    [
        (
            CanonicalState(
                location="clearing",
                food_scent_nearby=False,
                leaves_rustling=True,
                food_path_blocked=True,
            ),
            "You are in a clearing. You hear leaves rustling.",
        ),
        (
            CanonicalState(
                location="clearing",
                food_scent_nearby=True,
                leaves_rustling=False,
                food_path_blocked=True,
            ),
            "You are in a clearing. You smell food nearby.",
        ),
    ],
)
def test_accessible_substate_is_derived_from_canonical_observations(
    canonical_state: CanonicalState, expected_accessible: str
) -> None:
    calls: list[tuple[str, str, tuple[str, ...]]] = []

    async def complete(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls.append((accessible, profile, questions))
        return mediation("I will wait.", True, False, evidence="wait")

    trace = asyncio.run(run_turn(complete, canonical_state))

    assert calls == [(expected_accessible, EPISTEMIC_PROFILE, QUESTIONS)]
    assert trace.accessible_substate == expected_accessible
    assert "blocked" not in repr(calls[0]).lower()


def test_fixture_trace_is_json_safe_and_reproducible() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_causal_turn.yaml"
    case = load_corpus(corpus_path)[0]

    first = [asdict(trace) for trace in asyncio.run(run_fixture(case))]
    second = [asdict(trace) for trace in asyncio.run(run_fixture(case))]

    assert first == second
    assert first[0]["resolution"] == "food_path_blocked"
    assert first[0]["initial_canonical_state"] == {
        "location": "clearing",
        "food_scent_nearby": True,
        "leaves_rustling": True,
        "food_path_blocked": True,
    }
    assert first[0]["resulting_canonical_state"] == first[0]["initial_canonical_state"]
    json.dumps(first, sort_keys=True)


def test_replay_rejects_a_trace_with_a_changed_authoritative_outcome() -> None:
    async def complete(_: str, __: str, ___: tuple[str, ...]) -> str:
        return mediation("Food seems close.", False, True, evidence="Food")

    trace = asyncio.run(run_turn(complete))

    with pytest.raises(ValueError, match="does not match"):
        replay(replace(trace, resolution="waited"))
