"""Domain-opaque composition validation, execution, recording, and replay."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class CompositionError(ValueError):
    """A structural declaration or retained-record mismatch."""


@dataclass(frozen=True)
class ActorRun:
    cognition: str
    proposal: str


class ActorComponent(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def proposal_vocabulary(self) -> tuple[str, ...]: ...

    async def mediate(self, shown_input: str) -> ActorRun: ...


@dataclass(frozen=True)
class Resolution:
    order: tuple[str, ...]
    decisions: tuple[str, ...]
    transitions: tuple[str, ...]
    outcome: str
    feedback: dict[str, str]


class SimulationComponent(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def accepted_proposals(self) -> Mapping[str, tuple[str, ...]]: ...

    def observe(self, actor: str, canonical_state: Any) -> str: ...

    def resolve(self, canonical_state: Any, proposals: Mapping[str, str]) -> tuple[Any, Resolution]: ...


@dataclass(frozen=True)
class CompositionDeclaration:
    name: str
    simulation: SimulationComponent
    actors: Mapping[str, ActorComponent]
    proposal_pairings: Mapping[str, tuple[str, ...]]
    initial_state: Any


@dataclass(frozen=True)
class RecordedDeclaration:
    name: str
    simulation_name: str
    actor_names: dict[str, str]
    proposal_pairings: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class RecordedActor:
    component_name: str
    shown_input: str
    cognition: str
    proposal: str


@dataclass(frozen=True)
class CompositionTrace:
    declaration: RecordedDeclaration
    initial_state: Any
    actors: dict[str, RecordedActor]
    resolution: Resolution
    resulting_state: Any

    def as_json(self) -> dict[str, object]:
        return asdict(self)


def validate(declaration: CompositionDeclaration) -> None:
    actor_names = set(declaration.actors)
    pairing_names = set(declaration.proposal_pairings)
    if actor_names != pairing_names:
        raise CompositionError(
            f"declaration {declaration.name!r} names actors {sorted(actor_names)!r} but pairings {sorted(pairing_names)!r}"
        )
    if len({actor.name for actor in declaration.actors.values()}) != len(declaration.actors):
        raise CompositionError(f"declaration {declaration.name!r} repeats a supplied component name")

    for actor_name, actor in declaration.actors.items():
        paired = declaration.proposal_pairings[actor_name]
        if set(actor.proposal_vocabulary) != set(paired):
            raise CompositionError(
                f"declaration {declaration.name!r} component {actor.name!r} does not pair its declared vocabulary"
            )
        accepted = set(declaration.simulation.accepted_proposals.get(actor_name, ()))
        for proposal in paired:
            if proposal not in accepted:
                raise CompositionError(
                    f"declaration {declaration.name!r} component {actor.name!r} has unpaired proposal {proposal!r}"
                )


async def run(declaration: CompositionDeclaration) -> CompositionTrace:
    validate(declaration)
    observations = {
        actor_name: declaration.simulation.observe(actor_name, declaration.initial_state) for actor_name in declaration.actors
    }
    records: dict[str, RecordedActor] = {}
    proposals: dict[str, str] = {}
    for actor_name, actor in declaration.actors.items():
        actor_run = await actor.mediate(observations[actor_name])
        if actor_run.proposal not in declaration.proposal_pairings[actor_name]:
            raise CompositionError(
                f"declaration {declaration.name!r} component {actor.name!r} submitted an undeclared proposal"
            )
        records[actor_name] = RecordedActor(actor.name, observations[actor_name], actor_run.cognition, actor_run.proposal)
        proposals[actor_name] = actor_run.proposal
    resulting_state, resolution = declaration.simulation.resolve(declaration.initial_state, proposals)
    return CompositionTrace(_record_declaration(declaration), declaration.initial_state, records, resolution, resulting_state)


def replay(declaration: CompositionDeclaration, trace: CompositionTrace) -> CompositionTrace:
    validate(declaration)
    if trace.declaration != _record_declaration(declaration) or trace.initial_state != declaration.initial_state:
        raise CompositionError("trace does not match its recorded declaration or source state")
    if set(trace.actors) != set(declaration.actors):
        raise CompositionError("trace does not match its recorded actor membership")

    proposals: dict[str, str] = {}
    for actor_name, actor in declaration.actors.items():
        record = trace.actors[actor_name]
        if record.component_name != actor.name or record.shown_input != declaration.simulation.observe(
            actor_name, declaration.initial_state
        ):
            raise CompositionError("trace does not match its recorded actor-visible input")
        if record.proposal not in declaration.proposal_pairings[actor_name]:
            raise CompositionError("trace does not match its recorded proposal pairing")
        proposals[actor_name] = record.proposal
    resulting_state, resolution = declaration.simulation.resolve(declaration.initial_state, proposals)
    if resolution != trace.resolution or resulting_state != trace.resulting_state:
        raise CompositionError("trace does not match the authoritative resolution")
    return trace


def _record_declaration(declaration: CompositionDeclaration) -> RecordedDeclaration:
    return RecordedDeclaration(
        declaration.name,
        declaration.simulation.name,
        {actor_name: actor.name for actor_name, actor in declaration.actors.items()},
        {actor_name: tuple(pairing) for actor_name, pairing in declaration.proposal_pairings.items()},
    )
