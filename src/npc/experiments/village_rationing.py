import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

Actor = Literal["household_one", "household_two", "organisation"]
HouseholdProposal = Literal["claim_4", "wait"]
AllocationProposal = tuple[int, int]
Mediation = Callable[[str, str, tuple[str, str]], Awaitable[str]]


@dataclass(frozen=True)
class ActorDescription:
    epistemic_profile: str
    questions: tuple[str, str]


HOUSEHOLD_ONE_DESCRIPTION = ActorDescription(
    "You speak only for household one. Use your local circumstances, not information about other households.",
    ("Does your household need the fixed emergency-food claim?", "Can your household submit the fixed claim now?"),
)
HOUSEHOLD_TWO_DESCRIPTION = ActorDescription(
    "You speak only for household two. Use your local circumstances, not information about other households.",
    ("Does your household need the fixed emergency-food claim?", "Can your household submit the fixed claim now?"),
)
ORGANISATION_DESCRIPTION = ActorDescription(
    "You allocate only from the public claim ledger and the stated emergency-food reserve.",
    ("Does the ledger support a priority allocation?", "Does the stated reserve cover that allocation?"),
)


@dataclass(frozen=True)
class CanonicalState:
    reserve_units: int = 6
    committed_allocations: tuple[tuple[str, int], ...] = ()


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
    proposal: HouseholdProposal | AllocationProposal | None


@dataclass(frozen=True)
class TurnTrace:
    initial_canonical_state: CanonicalState
    household_one: ActorRecord
    household_two: ActorRecord
    organisation: ActorRecord
    claim_ledger: tuple[tuple[str, int, int], ...]
    allocation_proposal: AllocationProposal | None
    validation_decision: Literal["accepted", "rejected"]
    transitions: tuple[str, ...]
    resulting_canonical_state: CanonicalState
    feedback: dict[Actor, str]


def initial_state() -> CanonicalState:
    return CanonicalState()


async def run_turn(
    mediate_household_one: Mediation,
    mediate_household_two: Mediation,
    mediate_organisation: Mediation,
    canonical_state: CanonicalState | None = None,
) -> TurnTrace:
    initial = canonical_state or initial_state()
    _validate_source_state(initial)
    household_one = await _mediate_household(mediate_household_one, _household_one_observation(), HOUSEHOLD_ONE_DESCRIPTION)
    household_two = await _mediate_household(mediate_household_two, _household_two_observation(), HOUSEHOLD_TWO_DESCRIPTION)
    ledger = _claim_ledger(household_one, household_two)
    organisation = await _mediate_organisation(
        mediate_organisation, _organisation_observation(initial.reserve_units, ledger), ORGANISATION_DESCRIPTION
    )
    allocation = organisation.proposal if isinstance(organisation.proposal, tuple) else None
    decision, transitions, resulting, feedback = _resolve(initial, ledger, allocation)
    return TurnTrace(
        initial,
        household_one,
        household_two,
        organisation,
        ledger,
        allocation,
        decision,
        transitions,
        resulting,
        feedback,
    )


async def _mediate_household(mediate: Mediation, observation: str, description: ActorDescription) -> ActorRecord:
    raw_response = await mediate(observation, description.epistemic_profile, description.questions)
    percept, answers, raw_proposal = _validate_mediation(raw_response, description.questions)
    proposal: HouseholdProposal | None = None
    if raw_proposal in ("claim_4", "wait"):
        proposal = raw_proposal
    if proposal == "claim_4" and (len(answers) != 2 or not all(answer.answer for answer in answers)):
        proposal = "wait"
    return ActorRecord(observation, description, percept, description.questions, answers, proposal)


async def _mediate_organisation(mediate: Mediation, observation: str, description: ActorDescription) -> ActorRecord:
    raw_response = await mediate(observation, description.epistemic_profile, description.questions)
    percept, answers, raw_proposal = _validate_mediation(raw_response, description.questions)
    proposal = _allocation_proposal(raw_proposal)
    if len(answers) != 2 or not all(answer.answer for answer in answers):
        proposal = None
    return ActorRecord(observation, description, percept, description.questions, answers, proposal)


def _validate_mediation(
    raw_response: object, questions: tuple[str, str]
) -> tuple[str | None, tuple[Answer, ...], object | None]:
    if not isinstance(raw_response, str):
        return None, (), None
    try:
        record = json.loads(raw_response)
    except json.JSONDecodeError:
        return None, (), None
    if not isinstance(record, dict):
        return None, (), None
    percept, raw_answers = record.get("percept"), record.get("answers")
    if not isinstance(percept, str) or not percept.strip() or not isinstance(raw_answers, list) or len(raw_answers) != 2:
        return None, (), None
    answers: list[Answer] = []
    for question, raw_answer in zip(questions, raw_answers, strict=True):
        if not isinstance(raw_answer, dict):
            return None, (), None
        answer, evidence = raw_answer.get("answer"), raw_answer.get("evidence")
        if (
            raw_answer.get("question") != question
            or not isinstance(answer, bool)
            or not isinstance(evidence, str)
            or not evidence.strip()
            or evidence not in percept
        ):
            return None, (), None
        answers.append(Answer(question, answer, evidence))
    return percept, tuple(answers), record.get("proposal")


def _allocation_proposal(raw_proposal: object) -> AllocationProposal | None:
    if not isinstance(raw_proposal, dict) or set(raw_proposal) != {"household_one", "household_two"}:
        return None
    allocations = (raw_proposal["household_one"], raw_proposal["household_two"])
    if not _is_bounded_allocation_proposal(allocations):
        return None
    return cast(AllocationProposal, allocations)


def _is_bounded_allocation_proposal(proposal: object) -> bool:
    return (
        isinstance(proposal, tuple)
        and len(proposal) == 2
        and all(isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 4 for value in proposal)
    )


def _claim_ledger(household_one: ActorRecord, household_two: ActorRecord) -> tuple[tuple[str, int, int], ...]:
    claims: list[tuple[str, int, int]] = []
    if household_one.proposal == "claim_4":
        claims.append(("household_one", 4, 1))
    if household_two.proposal == "claim_4":
        claims.append(("household_two", 4, 2))
    return tuple(claims)


def _resolve(
    initial: CanonicalState, ledger: tuple[tuple[str, int, int], ...], proposal: AllocationProposal | None
) -> tuple[Literal["accepted", "rejected"], tuple[str, ...], CanonicalState, dict[Actor, str]]:
    expected = _priority_allocation(initial.reserve_units, ledger)
    if proposal is None or proposal != expected:
        return (
            "rejected",
            (),
            initial,
            {
                "household_one": "No emergency-food allocation was committed for your household.",
                "household_two": "No emergency-food allocation was committed for your household.",
                "organisation": "The allocation proposal was rejected.",
            },
        )
    allocations = (("household_one", proposal[0]), ("household_two", proposal[1]))
    resulting = CanonicalState(initial.reserve_units - sum(proposal), allocations)
    return (
        "accepted",
        ("priority_allocation_committed",),
        resulting,
        {
            "household_one": f"Your household receives {proposal[0]} emergency-food units.",
            "household_two": f"Your household receives {proposal[1]} emergency-food units.",
            "organisation": "The priority allocation was accepted.",
        },
    )


def _priority_allocation(reserve: int, ledger: tuple[tuple[str, int, int], ...]) -> AllocationProposal:
    available = reserve
    allocations = {"household_one": 0, "household_two": 0}
    for household, requested, _ in ledger:
        allocation = min(requested, available)
        allocations[household] = allocation
        available -= allocation
    return allocations["household_one"], allocations["household_two"]


def replay(trace: TurnTrace) -> TurnTrace:
    _validate_source_state(trace.initial_canonical_state)
    expected_ledger = _claim_ledger(trace.household_one, trace.household_two)
    if (
        trace.household_one.actor_description != HOUSEHOLD_ONE_DESCRIPTION
        or trace.household_two.actor_description != HOUSEHOLD_TWO_DESCRIPTION
        or trace.organisation.actor_description != ORGANISATION_DESCRIPTION
        or trace.household_one.accessible_substate != _household_one_observation()
        or trace.household_two.accessible_substate != _household_two_observation()
        or trace.claim_ledger != expected_ledger
        or trace.organisation.accessible_substate
        != _organisation_observation(trace.initial_canonical_state.reserve_units, expected_ledger)
        or trace.household_one.proposal not in ("claim_4", "wait", None)
        or trace.household_two.proposal not in ("claim_4", "wait", None)
        or (trace.organisation.proposal is not None and not _is_bounded_allocation_proposal(trace.organisation.proposal))
        or not _valid_record(trace.household_one, HOUSEHOLD_ONE_DESCRIPTION)
        or not _valid_record(trace.household_two, HOUSEHOLD_TWO_DESCRIPTION)
        or not _valid_record(trace.organisation, ORGANISATION_DESCRIPTION)
    ):
        raise ValueError("trace does not match its recorded actor inputs")
    proposal = trace.organisation.proposal if isinstance(trace.organisation.proposal, tuple) else None
    expected = _resolve(trace.initial_canonical_state, expected_ledger, proposal)
    if trace.allocation_proposal != proposal or expected != (
        trace.validation_decision,
        trace.transitions,
        trace.resulting_canonical_state,
        trace.feedback,
    ):
        raise ValueError("trace does not match the authoritative resolution")
    return trace


def _valid_record(record: ActorRecord, description: ActorDescription) -> bool:
    if record.questions != description.questions:
        return False
    if record.subjective_percept is None:
        return record.answers == () and record.proposal is None
    return (
        len(record.answers) == 2
        and tuple(answer.question for answer in record.answers) == description.questions
        and all(answer.evidence in record.subjective_percept for answer in record.answers)
    )


def _validate_source_state(state: CanonicalState) -> None:
    if state.reserve_units not in (4, 6) or state.committed_allocations:
        raise ValueError("village-rationing turn requires the accepted initial reserve state")


def _household_one_observation() -> str:
    return "Your household has no food for today; your two dependants need emergency rations."


def _household_two_observation() -> str:
    return "Your household has no food for today; your infant needs emergency rations."


def _organisation_observation(reserve: int, ledger: tuple[tuple[str, int, int], ...]) -> str:
    claims = "; ".join(f"{household} requests {requested} at priority tier {tier}" for household, requested, tier in ledger)
    return f"Emergency food reserve: {reserve} units. Public claim ledger: {claims or 'no submitted claims'}."


async def run_fixture(case: Mapping[str, object]) -> list[TurnTrace]:
    state = cast(Mapping[str, object], case["canonical_state"])
    canonical_state = CanonicalState(**cast(dict[str, object], dict(state)))  # type: ignore[arg-type]
    responses = cast(Mapping[str, object], case["mediation_responses"])

    async def household_one(_: str, __: str, ___: tuple[str, str]) -> str:
        return cast(str, responses["household_one"])

    async def household_two(_: str, __: str, ___: tuple[str, str]) -> str:
        return cast(str, responses["household_two"])

    async def organisation(_: str, __: str, ___: tuple[str, str]) -> str:
        return cast(str, responses["organisation"])

    return [await run_turn(household_one, household_two, organisation, canonical_state)]


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "village_rationing.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(_trace_json(trace), sort_keys=True))


def _trace_json(trace: TurnTrace) -> dict[str, object]:
    from dataclasses import asdict

    return cast(dict[str, object], asdict(trace))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
