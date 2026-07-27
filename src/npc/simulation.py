from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]


@dataclass
class Entity:
    identifier: str
    location: int
    tags: set[str]
    consumable: bool = False
    consumed: bool = False


@dataclass
class State:
    actor_id: str
    actor_location: int
    capabilities: set[str]
    entities: dict[str, Entity]


@dataclass(frozen=True)
class Proposal:
    kind: str
    actor_id: str
    destination: int | None = None
    target: str | None = None
    label: str = "action"


@dataclass(frozen=True)
class Outcome:
    accepted: bool
    narration: str


def load_scenario(path: Path) -> tuple[State, list[dict[str, Any]]]:
    scenario = yaml.safe_load(path.read_text())
    profile_path = path.parent / scenario["actor_profile"]
    profile = yaml.safe_load(profile_path.read_text())
    actor = scenario["actor"]
    entities = {
        item["id"]: Entity(
            identifier=item["id"],
            location=item["location"],
            tags=set(item.get("tags", [])),
            consumable=item.get("consumable", False),
        )
        for item in scenario["entities"]
    }
    state = State(
        actor_id=actor["id"],
        actor_location=actor["location"],
        capabilities=set(profile["capabilities"]),
        entities=entities,
    )
    return state, cast(list[dict[str, Any]], profile["rules"])


def resolve(state: State, proposal: Proposal) -> Outcome:
    if proposal.actor_id != state.actor_id:
        return _rejected(proposal, "unknown actor")
    if proposal.kind == "move":
        if "move" not in state.capabilities or proposal.destination is None:
            return _rejected(proposal, "movement is not permitted")
        old_location = state.actor_location
        state.actor_location = proposal.destination
        return Outcome(True, f"accepted {proposal.label}: {state.actor_id} moved from {old_location} to {proposal.destination}")
    if proposal.kind == "consume":
        target = state.entities.get(proposal.target or "")
        if "consume" not in state.capabilities or target is None or not target.consumable:
            return _rejected(proposal, "consumption is not permitted")
        if target.location != state.actor_location:
            return _rejected(proposal, "actor and target are not co-located")
        if target.consumed:
            return _rejected(proposal, "target is already consumed")
        target.consumed = True
        return Outcome(True, f"accepted {proposal.label}: {state.actor_id} consumed {target.identifier}")
    return _rejected(proposal, f"unsupported action '{proposal.kind}'")


def select_proposal(state: State, rules: list[dict[str, Any]]) -> Proposal | None:
    for rule in rules:
        if _matches(state, rule["when"]):
            return _proposal_from_rule(state, rule)
    return None


def _rejected(proposal: Proposal, reason: str) -> Outcome:
    return Outcome(False, f"rejected {proposal.label}: {reason}")


def _matches(state: State, condition: dict[str, Any]) -> bool:
    if "all" in condition:
        return all(_matches(state, item) for item in condition["all"])
    if "not" in condition:
        return not _matches(state, condition["not"])
    if "tag_exists" in condition:
        return _entity_with_tag(state, condition["tag_exists"]) is not None
    if "co_located_tag" in condition:
        entity = _entity_with_tag(state, condition["co_located_tag"])
        return entity is not None and entity.location == state.actor_location
    distance = condition["distance_to_tag_at_most"]
    entity = _entity_with_tag(state, distance["tag"])
    return entity is not None and abs(entity.location - state.actor_location) <= distance["distance"]


def _proposal_from_rule(state: State, rule: dict[str, Any]) -> Proposal:
    specification = rule["proposal"]
    label = rule["label"]
    kind = specification["kind"]
    if kind == "consume":
        target = _entity_with_tag(state, specification["target_tag"])
        return Proposal("consume", state.actor_id, target=target.identifier if target else None, label=label)
    if kind != "move":
        return Proposal(kind, state.actor_id, label=label)
    reference = _entity_with_tag(state, specification["relative_to"])
    if reference is None:
        return Proposal("move", state.actor_id, label=label)
    direction = 1 if reference.location > state.actor_location else -1
    if specification["direction"] == "away":
        direction *= -1
    return Proposal("move", state.actor_id, destination=state.actor_location + direction, label=label)


def _entity_with_tag(state: State, tag: str) -> Entity | None:
    return next((entity for entity in state.entities.values() if tag in entity.tags and not entity.consumed), None)
