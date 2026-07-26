import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

EPISTEMIC_PROFILE = (
    "You are hungry and cautious. You cannot see beyond the clearing or through obstacles. "
    "Treat smells and sounds as clues, not facts."
)
QUESTIONS = (
    "Do I believe an immediate threat is present?",
    "Do I believe the food is reachable by approaching?",
)
Proposal = Literal["approach_food", "wait"]
Resolution = Literal["food_path_blocked", "waited"]
Mediation = Callable[[str, str, tuple[str, ...]], Awaitable[str]]


@dataclass(frozen=True)
class CanonicalState:
    location: Literal["clearing"]
    food_scent_nearby: bool
    leaves_rustling: bool
    food_path_blocked: bool


@dataclass(frozen=True)
class Answer:
    question: str
    answer: bool
    evidence: str


@dataclass(frozen=True)
class TurnTrace:
    initial_canonical_state: CanonicalState
    accessible_substate: str
    epistemic_profile: str
    subjective_percept: str | None
    questions: tuple[str, ...]
    answers: tuple[Answer, ...]
    proposal: Proposal
    resolution: Resolution
    resulting_canonical_state: CanonicalState
    feedback: str


def initial_state() -> CanonicalState:
    return CanonicalState(
        location="clearing",
        food_scent_nearby=True,
        leaves_rustling=True,
        food_path_blocked=True,
    )


async def run_turn(mediate: Mediation, canonical_state: CanonicalState | None = None) -> TurnTrace:
    initial = canonical_state or initial_state()
    if initial.location != "clearing" or not initial.food_path_blocked:
        raise ValueError("fox causal turn requires the accepted blocked clearing state")

    accessible_substate = _derive_accessible_substate(initial)
    raw_response = await mediate(accessible_substate, EPISTEMIC_PROFILE, QUESTIONS)
    percept, answers = _validate_mediation(raw_response)
    proposal = _propose(answers) if percept is not None else "wait"
    resolution, resulting, feedback = resolve_proposal(initial, proposal)
    return TurnTrace(
        initial_canonical_state=initial,
        accessible_substate=accessible_substate,
        epistemic_profile=EPISTEMIC_PROFILE,
        subjective_percept=percept,
        questions=QUESTIONS,
        answers=answers,
        proposal=proposal,
        resolution=resolution,
        resulting_canonical_state=resulting,
        feedback=feedback,
    )


def resolve_proposal(canonical_state: CanonicalState, proposal: object) -> tuple[Resolution, CanonicalState, str]:
    if proposal == "approach_food" and canonical_state.food_path_blocked:
        return "food_path_blocked", canonical_state, "The path to the food is blocked."
    return "waited", canonical_state, "The fox waited."


def replay(trace: TurnTrace) -> TurnTrace:
    if (
        trace.accessible_substate != _derive_accessible_substate(trace.initial_canonical_state)
        or trace.epistemic_profile != EPISTEMIC_PROFILE
        or trace.questions != QUESTIONS
    ):
        raise ValueError("trace does not match the accepted fox causal-turn input")
    resolution, resulting, feedback = resolve_proposal(trace.initial_canonical_state, trace.proposal)
    if (resolution, resulting, feedback) != (
        trace.resolution,
        trace.resulting_canonical_state,
        trace.feedback,
    ):
        raise ValueError("trace does not match the authoritative resolution")
    return trace


async def run_fixture(case: Mapping[str, object]) -> list[TurnTrace]:
    response = cast(str, case["mediation_response"])
    state = cast(Mapping[str, object], case["canonical_state"])
    canonical_state = CanonicalState(
        location=cast(Literal["clearing"], state["location"]),
        food_scent_nearby=cast(bool, state["food_scent_nearby"]),
        leaves_rustling=cast(bool, state["leaves_rustling"]),
        food_path_blocked=cast(bool, state["food_path_blocked"]),
    )

    async def mediate(_: str, __: str, ___: tuple[str, ...]) -> str:
        return response

    return [await run_turn(mediate, canonical_state)]


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


def _validate_mediation(raw_response: str) -> tuple[str | None, tuple[Answer, ...]]:
    try:
        record = json.loads(raw_response)
    except json.JSONDecodeError:
        return None, ()
    if not isinstance(record, dict):
        return None, ()
    percept = record.get("percept")
    raw_answers = record.get("answers")
    if not isinstance(percept, str) or not percept.strip():
        return None, ()
    if not isinstance(raw_answers, list) or len(raw_answers) != len(QUESTIONS):
        return None, ()
    answers: list[Answer] = []
    for question, raw_answer in zip(QUESTIONS, raw_answers, strict=True):
        if not isinstance(raw_answer, dict):
            return None, ()
        answer = raw_answer.get("answer")
        evidence = raw_answer.get("evidence")
        if (
            raw_answer.get("question") != question
            or not isinstance(answer, bool)
            or not isinstance(evidence, str)
            or not evidence.strip()
            or evidence not in percept
        ):
            return None, ()
        answers.append(Answer(question=question, answer=answer, evidence=evidence))
    return percept, tuple(answers)


def _propose(answers: tuple[Answer, ...]) -> Proposal:
    if answers[0].answer is False and answers[1].answer is True:
        return "approach_food"
    return "wait"


def _derive_accessible_substate(canonical_state: CanonicalState) -> str:
    observations = ["You are in a clearing."]
    if canonical_state.food_scent_nearby:
        observations.append("You smell food nearby.")
    if canonical_state.leaves_rustling:
        observations.append("You hear leaves rustling.")
    return " ".join(observations)


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_causal_turn.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(_trace_json(trace), sort_keys=True))


def _trace_json(trace: TurnTrace) -> dict[str, object]:
    return {
        "initial_canonical_state": trace.initial_canonical_state.__dict__,
        "accessible_substate": trace.accessible_substate,
        "epistemic_profile": trace.epistemic_profile,
        "subjective_percept": trace.subjective_percept,
        "questions": trace.questions,
        "answers": [answer.__dict__ for answer in trace.answers],
        "proposal": trace.proposal,
        "resolution": trace.resolution,
        "resulting_canonical_state": trace.resulting_canonical_state.__dict__,
        "feedback": trace.feedback,
    }


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
