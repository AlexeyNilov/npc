from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, cast

World = TypeVar("World")
Profile = TypeVar("Profile")
View = TypeVar("View")
Proposal = TypeVar("Proposal")
Outcome = TypeVar("Outcome")
WorldContra = TypeVar("WorldContra", contravariant=True)
WorldInvariant = TypeVar("WorldInvariant")
ProfileContra = TypeVar("ProfileContra", contravariant=True)
ViewContra = TypeVar("ViewContra", contravariant=True)
ViewCo = TypeVar("ViewCo", covariant=True)
ProposalContra = TypeVar("ProposalContra", contravariant=True)
ProposalCo = TypeVar("ProposalCo", covariant=True)
OutcomeCo = TypeVar("OutcomeCo", covariant=True)
OutcomeContra = TypeVar("OutcomeContra", contravariant=True)

Completion = Callable[[str, str], Awaitable[str]]


class MediationError(ValueError):
    """An actor's binary answers could not cross the mediation boundary."""


class Scheduler(Protocol[WorldContra]):
    def next_participant(self, world: WorldContra, participants: tuple[str, ...]) -> str | None: ...


class AccessPolicy(Protocol[WorldContra, ProfileContra, ViewCo]):
    def view_for(self, world: WorldContra, participant: str, profile: ProfileContra) -> ViewCo: ...


class DecisionPolicy(Protocol[ProfileContra, ViewContra, ProposalCo]):
    def questions_for(self, profile: ProfileContra, view: ViewContra) -> tuple[str, ...]: ...

    def propose(self, profile: ProfileContra, view: ViewContra, answers: Mapping[str, bool]) -> ProposalCo: ...


class Mediator(Protocol[ViewContra]):
    async def answer(self, view: ViewContra, questions: tuple[str, ...]) -> Mapping[str, bool]: ...


class Resolver(Protocol[WorldInvariant, ProposalContra, OutcomeCo]):
    def resolve(
        self, world: WorldInvariant, participant: str, proposal: ProposalContra
    ) -> tuple[WorldInvariant, OutcomeCo]: ...


@dataclass(frozen=True)
class TurnRecord[View, Proposal, Outcome]:
    participant: str
    accessible_view: View
    answers: tuple[tuple[str, bool], ...]
    proposal: Proposal
    outcome: Outcome


class Presenter(Protocol[ViewContra, ProposalContra, OutcomeContra]):
    async def present(self, record: TurnRecord[ViewContra, ProposalContra, OutcomeContra]) -> str: ...


@dataclass(frozen=True)
class TurnResult[View, Proposal, Outcome]:
    record: TurnRecord[View, Proposal, Outcome]
    presentation: str | None


@dataclass
class SimulationBuilder[World, Profile, View, Proposal, Outcome]:
    world: World
    profiles: Mapping[str, Profile]
    scheduler: Scheduler[World]
    access_policy: AccessPolicy[World, Profile, View]
    decision_policy: DecisionPolicy[Profile, View, Proposal]
    mediator: Mediator[View]
    resolver: Resolver[World, Proposal, Outcome]
    presenter: Presenter[View, Proposal, Outcome] | None = None

    def build(self) -> Simulation[World, Profile, View, Proposal, Outcome]:
        if not self.profiles:
            raise ValueError("a simulation requires at least one participant profile")
        return Simulation(
            _world=_snapshot(self.world),
            profiles=dict(self.profiles),
            scheduler=self.scheduler,
            access_policy=self.access_policy,
            decision_policy=self.decision_policy,
            mediator=self.mediator,
            resolver=self.resolver,
            presenter=self.presenter,
        )


@dataclass
class Simulation[World, Profile, View, Proposal, Outcome]:
    _world: World
    profiles: dict[str, Profile]
    scheduler: Scheduler[World]
    access_policy: AccessPolicy[World, Profile, View]
    decision_policy: DecisionPolicy[Profile, View, Proposal]
    mediator: Mediator[View]
    resolver: Resolver[World, Proposal, Outcome]
    presenter: Presenter[View, Proposal, Outcome] | None = None
    _history: list[TurnRecord[View, Proposal, Outcome]] = field(default_factory=list, init=False)

    @property
    def world(self) -> World:
        return _snapshot(self._world)

    @property
    def history(self) -> tuple[TurnRecord[View, Proposal, Outcome], ...]:
        return tuple(_snapshot(record) for record in self._history)

    async def run_next(self) -> TurnResult[View, Proposal, Outcome] | None:
        participant = self.scheduler.next_participant(_snapshot(self._world), tuple(self.profiles))
        if participant is None:
            return None
        profile = self.profiles.get(participant)
        if profile is None:
            raise ValueError(f"scheduler selected unknown participant {participant!r}")
        view = self.access_policy.view_for(_snapshot(self._world), participant, profile)
        questions = self.decision_policy.questions_for(profile, view)
        answers = _validated_answers(await self.mediator.answer(view, questions), questions)
        proposal = self.decision_policy.propose(profile, view, answers)
        next_world, outcome = self.resolver.resolve(_snapshot(self._world), participant, proposal)
        self._world = _snapshot(next_world)
        record = TurnRecord(
            participant,
            _snapshot(view),
            tuple((question, answers[question]) for question in questions),
            _snapshot(proposal),
            _snapshot(outcome),
        )
        self._history.append(record)
        return TurnResult(_snapshot(record), await self._present(record))

    async def _present(self, record: TurnRecord[View, Proposal, Outcome]) -> str | None:
        if self.presenter is None:
            return None
        try:
            presentation = await self.presenter.present(_snapshot(record))
        except Exception:
            return None
        return presentation.strip() or None


@dataclass(frozen=True)
class LanguageModelMediator:
    completion: Completion

    async def answer(self, view: object, questions: tuple[str, ...]) -> Mapping[str, bool]:
        if not questions:
            return {}
        prompt = json.dumps({"questions": questions, "accessible_view": view}, sort_keys=True)
        try:
            response = await self.completion(
                prompt,
                "Answer every listed question using only the accessible view. "
                "Return only a JSON object whose keys are exactly the question texts and whose values are JSON booleans.",
            )
        except Exception as error:
            raise MediationError(f"mediation request failed: {error}") from error
        try:
            parsed = json.loads(_json_response_body(response))
        except json.JSONDecodeError as error:
            raise MediationError(f"mediation response is malformed JSON: {response[:1000]!r}") from error
        if not isinstance(parsed, dict):
            raise MediationError("mediation response must be a JSON object")
        return _validated_answers(cast(Mapping[str, object], parsed), questions)


def _validated_answers(answers: Mapping[str, object], questions: tuple[str, ...]) -> dict[str, bool]:
    if set(answers) != set(questions):
        raise MediationError("mediation response must contain exactly the declared questions")
    if any(type(answer) is not bool for answer in answers.values()):
        raise MediationError("mediation response values must be JSON booleans")
    return {question: cast(bool, answers[question]) for question in questions}


def _json_response_body(response: str) -> str:
    lines = response.strip().splitlines()
    if len(lines) >= 3 and lines[0].strip().lower() == "```json" and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1])
    return response.strip()


def _snapshot[Snapshot](value: Snapshot) -> Snapshot:
    return cast(Snapshot, deepcopy(value))
