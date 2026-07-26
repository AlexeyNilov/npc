import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

Actor = Literal["fox", "hunter"]
FoxProposal = Literal["approach_food", "wait"]
HunterProposal = Literal["set_trap", "wait"]
Proposal = FoxProposal | HunterProposal
Outcome = Literal["fox_caught_by_trap", "fox_reaches_food", "waited"]
Mediation = Callable[[str, str, tuple[str, ...]], Awaitable[str]]


@dataclass(frozen=True)
class ActorDescription:
    epistemic_profile: str
    questions: tuple[str, str]
    proposal_vocabulary: tuple[Proposal, ...]


FOX_DESCRIPTION = ActorDescription(
    "You are hungry and cautious. You cannot see a concealed hunter or a hidden trap. "
    "Treat smells and apparent quiet as clues, not facts.",
    (
        "Do I believe an immediate threat is present?",
        "Do I believe the food is reachable by approaching?",
    ),
    ("approach_food", "wait"),
)
HUNTER_DESCRIPTION = ActorDescription(
    "You are a patient hunter. Fresh tracks are clues to likely movement, not proof of the fox's current position.",
    (
        "Do I believe a fox is likely to approach the food this turn?",
        "Do I believe I can set the trap now?",
    ),
    ("set_trap", "wait"),
)


@dataclass(frozen=True)
class CanonicalState:
    fox_location: Literal["clearing_edge", "food"] = "clearing_edge"
    hunter_location: Literal["beside_clearing"] = "beside_clearing"
    hunter_concealed: bool = True
    fox_tracks_lead_to_food: bool = True
    food_available: bool = True
    trap_set: bool = False
    trap_materials_ready: bool = True
    fox_caught: bool = False
    food_consumed: bool = False


@dataclass(frozen=True)
class Answer:
    question: str
    answer: bool
    evidence: str


@dataclass(frozen=True)
class ActorRecord:
    accessible_substate: str
    actor_description: ActorDescription
    subjective_percept: str | None
    questions: tuple[str, str]
    answers: tuple[Answer, ...]
    proposal: Proposal


@dataclass(frozen=True)
class TurnTrace:
    initial_canonical_state: CanonicalState
    fox: ActorRecord
    hunter: ActorRecord
    resolution_order: tuple[Actor, Actor]
    decisions: tuple[str, ...]
    transitions: tuple[str, ...]
    resulting_canonical_state: CanonicalState
    outcome: Outcome
    feedback: dict[Actor, str]


def initial_state() -> CanonicalState:
    return CanonicalState()


async def run_turn(
    mediate_fox: Mediation,
    mediate_hunter: Mediation,
    canonical_state: CanonicalState | None = None,
) -> TurnTrace:
    initial = canonical_state or initial_state()
    _validate_source_state(initial)
    fox_observation = _fox_observation(initial)
    hunter_observation = _hunter_observation(initial)
    fox_record = await _mediate(mediate_fox, fox_observation, FOX_DESCRIPTION, "fox")
    hunter_record = await _mediate(mediate_hunter, hunter_observation, HUNTER_DESCRIPTION, "hunter")
    decisions, transitions, resulting, outcome, feedback = _resolve(initial, hunter_record.proposal, fox_record.proposal)
    return TurnTrace(
        initial, fox_record, hunter_record, ("hunter", "fox"), decisions, transitions, resulting, outcome, feedback
    )


async def _mediate(mediate: Mediation, observation: str, description: ActorDescription, actor: Actor) -> ActorRecord:
    raw_response = await mediate(observation, description.epistemic_profile, description.questions)
    percept, answers = _validate_mediation(raw_response, description.questions)
    proposal = _propose(actor, answers) if percept is not None else "wait"
    return ActorRecord(observation, description, percept, description.questions, answers, proposal)


def _validate_mediation(raw_response: object, questions: tuple[str, str]) -> tuple[str | None, tuple[Answer, ...]]:
    if not isinstance(raw_response, str):
        return None, ()
    try:
        record = json.loads(raw_response)
    except json.JSONDecodeError:
        return None, ()
    if not isinstance(record, dict):
        return None, ()
    percept, raw_answers = record.get("percept"), record.get("answers")
    if not isinstance(percept, str) or not percept.strip() or not isinstance(raw_answers, list) or len(raw_answers) != 2:
        return None, ()
    answers: list[Answer] = []
    for question, raw_answer in zip(questions, raw_answers, strict=True):
        if not isinstance(raw_answer, dict):
            return None, ()
        answer, evidence = raw_answer.get("answer"), raw_answer.get("evidence")
        if (
            raw_answer.get("question") != question
            or not isinstance(answer, bool)
            or not isinstance(evidence, str)
            or not evidence.strip()
            or evidence not in percept
        ):
            return None, ()
        answers.append(Answer(question, answer, evidence))
    return percept, tuple(answers)


def _propose(actor: Actor, answers: tuple[Answer, ...]) -> Proposal:
    if len(answers) != 2:
        return "wait"
    if actor == "fox" and answers[0].answer is False and answers[1].answer is True:
        return "approach_food"
    if actor == "hunter" and answers[0].answer is True and answers[1].answer is True:
        return "set_trap"
    return "wait"


def _resolve(
    initial: CanonicalState, hunter_proposal: Proposal, fox_proposal: Proposal
) -> tuple[tuple[str, ...], tuple[str, ...], CanonicalState, Outcome, dict[Actor, str]]:
    state = initial
    decisions: list[str] = [cast(str, hunter_proposal)]
    transitions: list[str] = []
    if hunter_proposal == "set_trap" and initial.trap_materials_ready:
        state = _replace(state, trap_set=True)
        transitions.append("trap_set")
    decisions.append(cast(str, fox_proposal))
    if fox_proposal == "approach_food" and state.trap_set:
        state = _replace(state, fox_caught=True)
        transitions.append("fox_caught")
        return (
            tuple(decisions[:-1]) + ("fox_caught_by_trap",),
            tuple(transitions),
            state,
            "fox_caught_by_trap",
            {"fox": "A hidden trap catches you as you reach the food.", "hunter": "Your trap catches the fox."},
        )
    if fox_proposal == "approach_food":
        state = _replace(state, fox_location="food", food_consumed=True)
        transitions.extend(("fox_moves_to_food", "food_consumed"))
        return (
            tuple(decisions),
            tuple(transitions),
            state,
            "fox_reaches_food",
            {"fox": "You reach the food.", "hunter": "The fox reaches the food."},
        )
    return (
        tuple(decisions),
        tuple(transitions),
        state,
        "waited",
        {"fox": "You wait.", "hunter": "The fox does not reach the food."},
    )


def _replace(state: CanonicalState, **changes: object) -> CanonicalState:
    values = state.__dict__ | changes
    return CanonicalState(**values)


def replay(trace: TurnTrace) -> TurnTrace:
    _validate_source_state(trace.initial_canonical_state)
    if (
        trace.resolution_order != ("hunter", "fox")
        or trace.fox.actor_description != FOX_DESCRIPTION
        or trace.hunter.actor_description != HUNTER_DESCRIPTION
        or trace.fox.accessible_substate != _fox_observation(trace.initial_canonical_state)
        or trace.hunter.accessible_substate != _hunter_observation(trace.initial_canonical_state)
        or trace.fox.proposal not in FOX_DESCRIPTION.proposal_vocabulary
        or trace.hunter.proposal not in HUNTER_DESCRIPTION.proposal_vocabulary
    ):
        raise ValueError("trace does not match its recorded actor inputs")
    expected = _resolve(trace.initial_canonical_state, trace.hunter.proposal, trace.fox.proposal)
    if expected != (trace.decisions, trace.transitions, trace.resulting_canonical_state, trace.outcome, trace.feedback):
        raise ValueError("trace does not match the authoritative resolution")
    return trace


def _validate_source_state(state: CanonicalState) -> None:
    if (
        state.fox_location != "clearing_edge"
        or state.hunter_location != "beside_clearing"
        or not state.hunter_concealed
        or not state.fox_tracks_lead_to_food
        or not state.food_available
        or state.trap_set
        or state.fox_caught
        or state.food_consumed
    ):
        raise ValueError("shared-world turn requires the accepted initial clearing state")


def _fox_observation(_: CanonicalState) -> str:
    return "You are at the edge of a clearing. You smell food in the clearing. The clearing appears quiet."


def _hunter_observation(state: CanonicalState) -> str:
    readiness = "ready" if state.trap_materials_ready else "not ready"
    return f"You are concealed beside a clearing. Fresh fox tracks lead toward food. Your trap materials are {readiness}."


async def run_fixture(case: Mapping[str, object]) -> list[TurnTrace]:
    state = cast(Mapping[str, object], case["canonical_state"])
    canonical_state = CanonicalState(**cast(dict[str, object], dict(state)))  # type: ignore[arg-type]
    responses = cast(Mapping[str, object], case["mediation_responses"])

    async def fox(_: str, __: str, ___: tuple[str, ...]) -> str:
        return cast(str, responses["fox"])

    async def hunter(_: str, __: str, ___: tuple[str, ...]) -> str:
        return cast(str, responses["hunter"])

    return [await run_turn(fox, hunter, canonical_state)]


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


def _trace_json(trace: TurnTrace) -> dict[str, object]:
    return {
        "initial_canonical_state": trace.initial_canonical_state.__dict__,
        "fox": {
            **trace.fox.__dict__,
            "actor_description": trace.fox.actor_description.__dict__,
            "answers": [a.__dict__ for a in trace.fox.answers],
        },
        "hunter": {
            **trace.hunter.__dict__,
            "actor_description": trace.hunter.actor_description.__dict__,
            "answers": [a.__dict__ for a in trace.hunter.answers],
        },
        "resolution_order": trace.resolution_order,
        "decisions": trace.decisions,
        "transitions": trace.transitions,
        "resulting_canonical_state": trace.resulting_canonical_state.__dict__,
        "outcome": trace.outcome,
        "feedback": trace.feedback,
    }


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_hunter_shared_world.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(_trace_json(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
