import asyncio
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from npc.experiments.fox_causal_turn import (
    FOX_DESCRIPTION,
    ActorDescription,
    CanonicalState,
    load_corpus,
    replay,
    resolve_proposal,
    run_fixture,
    run_turn,
)


def mediation(
    percept: str,
    threat: bool,
    reachable: bool,
    *,
    description: ActorDescription = FOX_DESCRIPTION,
    evidence: str | None = None,
) -> str:
    return json.dumps(
        {
            "percept": percept,
            "answers": [
                {"question": description.questions[0], "answer": threat, "evidence": evidence or percept},
                {"question": description.questions[1], "answer": reachable, "evidence": evidence or percept},
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

    assert calls == [
        (
            "You are in a clearing. You smell food nearby. You hear leaves rustling.",
            FOX_DESCRIPTION.epistemic_profile,
            FOX_DESCRIPTION.questions,
        )
    ]
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
    assert [answer.question for answer in trace.answers] == list(FOX_DESCRIPTION.questions)
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
                    {"question": FOX_DESCRIPTION.questions[0], "answer": False, "evidence": "Food"},
                    {"question": FOX_DESCRIPTION.questions[1], "answer": True, "evidence": "missing"},
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

    assert calls == [(expected_accessible, FOX_DESCRIPTION.epistemic_profile, FOX_DESCRIPTION.questions)]
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


def test_actor_description_variation_changes_only_actor_facing_mediation_and_proposal_inputs() -> None:
    description = ActorDescription(
        epistemic_profile="You are a cautious observer.",
        questions=("Is the clearing safe?", "Is the food worth approaching?"),
        proposal_vocabulary=("wait",),
        retained_context=(),
    )
    calls: list[tuple[str, str, tuple[str, ...]]] = []

    async def complete(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls.append((accessible, profile, questions))
        return mediation(
            "The clearing seems quiet and food seems close.", False, True, description=description, evidence="seems"
        )

    trace = asyncio.run(run_turn(complete, actor_description=description))

    assert calls == [
        (
            "You are in a clearing. You smell food nearby. You hear leaves rustling.",
            description.epistemic_profile,
            description.questions,
        )
    ]
    assert trace.actor_description == description
    assert trace.proposal == "wait"
    assert trace.resolution == "waited"
    assert replay(trace) == trace
    assert resolve_proposal(trace.initial_canonical_state, "approach_food")[0] == "food_path_blocked"


def test_contrasting_actor_description_withholds_blocked_path_from_mediation() -> None:
    crow = ActorDescription(
        epistemic_profile=(
            "You are an alert crow looking for food. You may assess what you can observe from above, "
            "but you do not know what lies behind obstacles or beyond your view. "
            "Treat sounds and smells as clues, not facts."
        ),
        questions=(
            "Do I believe the clearing is safe to enter?",
            "Do I believe the food is worth investigating from here?",
        ),
        proposal_vocabulary=("approach_food", "wait"),
        retained_context=(),
    )
    calls: list[tuple[str, str, tuple[str, ...]]] = []

    async def complete(accessible: str, profile: str, questions: tuple[str, ...]) -> str:
        calls.append((accessible, profile, questions))
        return mediation(
            "The clearing seems quiet and food seems worth investigating.", False, True, description=crow, evidence="seems"
        )

    trace = asyncio.run(run_turn(complete, actor_description=crow))

    assert calls == [
        (
            "You are in a clearing. You smell food nearby. You hear leaves rustling.",
            crow.epistemic_profile,
            crow.questions,
        )
    ]
    assert "food_path_blocked" not in repr(calls[0]).lower()
    assert "blocked" not in calls[0][0].lower()
    assert trace.resolution == "food_path_blocked"
