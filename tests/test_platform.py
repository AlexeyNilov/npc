from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

from npc.platform import LanguageModelMediator, MediationError, Presenter, SimulationBuilder, TurnRecord


@dataclass(frozen=True)
class World:
    value: int = 0


@dataclass(frozen=True)
class Profile:
    question: str


@dataclass(frozen=True)
class Proposal:
    change: int


@dataclass(frozen=True)
class Outcome:
    accepted: bool


class SequenceScheduler:
    def __init__(self, participants: list[str]) -> None:
        self._participants = iter(participants)

    def next_participant(self, world: World, participants: tuple[str, ...]) -> str | None:
        return next(self._participants, None)


class Views:
    def view_for(self, world: World, participant: str, profile: Profile) -> dict[str, object]:
        return {"participant": participant, "visible_value": world.value}


class Policies:
    def questions_for(self, profile: Profile, view: dict[str, object]) -> tuple[str, ...]:
        return (profile.question,)

    def propose(self, profile: Profile, view: dict[str, object], answers: Mapping[str, bool]) -> Proposal:
        return Proposal(1 if answers[profile.question] else 0)


class Answers:
    def __init__(self, answers: list[dict[str, bool]]) -> None:
        self._answers = iter(answers)
        self.seen: list[tuple[dict[str, object], tuple[str, ...]]] = []

    async def answer(self, view: dict[str, object], questions: tuple[str, ...]) -> dict[str, bool]:
        self.seen.append((view, questions))
        return next(self._answers)


class Resolver:
    def __init__(self) -> None:
        self.calls: list[tuple[World, str, Proposal]] = []

    def resolve(self, world: World, participant: str, proposal: Proposal) -> tuple[World, Outcome]:
        self.calls.append((world, participant, proposal))
        if proposal.change == 0:
            return world, Outcome(False)
        return World(world.value + proposal.change), Outcome(True)


def _simulation(answers: Answers, resolver: Resolver, presenter: Presenter[dict[str, object], Proposal, Outcome] | None = None):
    return SimulationBuilder(
        world=World(),
        profiles={"alpha": Profile("Advance?"), "beta": Profile("Respond?")},
        scheduler=SequenceScheduler(["alpha", "beta"]),
        access_policy=Views(),
        decision_policy=Policies(),
        mediator=answers,
        resolver=resolver,
        presenter=presenter,
    ).build()


def test_engine_coordinates_two_participants_and_retains_canonical_records() -> None:
    answers = Answers([{"Advance?": True}, {"Respond?": False}])
    resolver = Resolver()
    simulation = _simulation(answers, resolver)

    first = asyncio.run(simulation.run_next())
    second = asyncio.run(simulation.run_next())

    assert first is not None and second is not None
    assert simulation.world == World(1)
    assert [record.participant for record in simulation.history] == ["alpha", "beta"]
    assert first.record.accessible_view == {"participant": "alpha", "visible_value": 0}
    assert second.record.accessible_view == {"participant": "beta", "visible_value": 1}
    assert first.record.answers == (("Advance?", True),)
    assert first.record.proposal == Proposal(1)
    assert first.record.outcome == Outcome(True)
    assert second.record.outcome == Outcome(False)
    assert [call[0] for call in resolver.calls] == [World(0), World(1)]


def test_invalid_mediation_stops_before_resolution() -> None:
    answers = Answers([{"Advance?": "yes"}])  # type: ignore[dict-item]
    resolver = Resolver()
    simulation = _simulation(answers, resolver)

    with pytest.raises(MediationError, match="JSON booleans"):
        asyncio.run(simulation.run_next())

    assert simulation.world == World()
    assert simulation.history == ()
    assert resolver.calls == []


def test_presentation_failure_cannot_hide_completed_turn() -> None:
    class BrokenPresenter:
        async def present(self, record: TurnRecord[dict[str, object], Proposal, Outcome]) -> str:
            raise RuntimeError("offline")

    answers = Answers([{"Advance?": True}, {"Respond?": False}])
    simulation = _simulation(answers, Resolver(), BrokenPresenter())

    result = asyncio.run(simulation.run_next())

    assert result is not None
    assert result.presentation is None
    assert simulation.world == World(1)
    assert simulation.history == (result.record,)


def test_language_mediator_batches_questions_and_requires_an_exact_boolean_mapping() -> None:
    requests: list[tuple[str, str]] = []

    async def complete(prompt: str, instructions: str) -> str:
        requests.append((prompt, instructions))
        return "```json\n" + json.dumps({"Is it safe?": True, "Is it useful?": False}) + "\n```"

    answers = asyncio.run(LanguageModelMediator(complete).answer({"visible": "only this"}, ("Is it safe?", "Is it useful?")))

    assert answers == {"Is it safe?": True, "Is it useful?": False}
    assert json.loads(requests[0][0]) == {
        "accessible_view": {"visible": "only this"},
        "questions": ["Is it safe?", "Is it useful?"],
    }
    assert "exactly" in requests[0][1]
