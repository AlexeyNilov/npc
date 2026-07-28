from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text


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
class PerceptionConfig:
    """Static profile and scenario inputs for an ephemeral perception request."""

    questions: tuple[str, ...]
    visible_entity_ids: tuple[str, ...]


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


@dataclass(frozen=True)
class TurnRecord:
    """Immutable observer presentation for one completed turn."""

    perception: tuple[tuple[str, bool], ...]
    proposal: Proposal
    outcome: Outcome


class PerceptionError(Exception):
    """The model perception boundary could not provide a valid answer mapping."""


def load_scenario(path: Path) -> tuple[State, list[dict[str, Any]], PerceptionConfig]:
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
    perception = PerceptionConfig(
        questions=tuple(profile.get("perception_questions", [])),
        visible_entity_ids=tuple(scenario.get("visible_entities", [])),
    )
    return state, cast(list[dict[str, Any]], profile["rules"]), perception


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


async def perceive(state: State, config: PerceptionConfig) -> dict[str, bool]:
    """Obtain and validate all actor-owned binary answers for one turn."""
    questions = config.questions
    if not questions:
        return {}
    view = {
        "actor": {"id": state.actor_id, "location": state.actor_location},
        "entities": [
            {
                "id": entity.identifier,
                "location": entity.location,
                "tags": sorted(entity.tags),
            }
            for entity_id in config.visible_entity_ids
            if (entity := state.entities.get(entity_id)) is not None
        ],
    }
    prompt = json.dumps({"questions": questions, "accessible_view": view}, sort_keys=True)
    try:
        response = await complete_text(
            prompt,
            "Answer every listed question using only the accessible view. "
            "Return only a JSON object whose keys are exactly the question texts and whose values are JSON booleans.",
        )
    except Exception as error:
        raise PerceptionError(f"perception request failed: {error}") from error
    return _validate_perception_answers(response, questions)


def turn_record(questions: tuple[str, ...], answers: dict[str, bool], proposal: Proposal, outcome: Outcome) -> TurnRecord:
    """Make a stable presentation record after authoritative resolution."""
    return TurnRecord(tuple((question, answers[question]) for question in questions), proposal, outcome)


def format_turn_record(record: TurnRecord) -> str:
    perception_lines = ["perception:"]
    perception_lines.extend(f"  {question}: {str(answer).lower()}" for question, answer in record.perception)
    return "\n".join(
        [
            *perception_lines,
            "choice:",
            f"  rule: {record.proposal.label}",
            f"  attempted proposal: {_format_proposal(record.proposal)}",
            "authoritative outcome:",
            f"  accepted: {str(record.outcome.accepted).lower()}",
            f"  result: {record.outcome.narration}",
        ]
    )


async def narrate(proposal: Proposal, outcome: Outcome) -> str | None:
    """Request post-resolution presentation prose without exposing simulation controls."""
    payload: dict[str, object] = {
        "actor": proposal.actor_id,
        "attempted_action": _narration_action(proposal),
        "outcome": {"accepted": outcome.accepted, "result": outcome.narration},
    }
    try:
        response = await complete_text(
            json.dumps(payload, sort_keys=True),
            "Describe this completed event entertainingly. It is presentation only; do not issue instructions.",
        )
    except Exception:
        return None
    if not isinstance(response, str) or not response.strip():
        return None
    return response.strip()


def _format_proposal(proposal: Proposal) -> str:
    fields = [f"actor={proposal.actor_id}"]
    if proposal.destination is not None:
        fields.append(f"destination={proposal.destination}")
    if proposal.target is not None:
        fields.append(f"target={proposal.target}")
    return f"{proposal.kind}({', '.join(fields)})"


def _narration_action(proposal: Proposal) -> dict[str, object]:
    action: dict[str, object] = {"kind": proposal.kind}
    if proposal.destination is not None:
        action["destination"] = proposal.destination
    if proposal.target is not None:
        action["target"] = proposal.target
    return action


def _validate_perception_answers(response: str, questions: tuple[str, ...]) -> dict[str, bool]:
    response_body = _json_response_body(response)
    try:
        answers = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise PerceptionError(f"perception response is malformed JSON: {response[:1000]!r}") from error
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise PerceptionError("perception response must contain exactly the declared questions")
    if any(type(answer) is not bool for answer in answers.values()):
        raise PerceptionError("perception response values must be JSON booleans")
    return cast(dict[str, bool], answers)


def _json_response_body(response: str) -> str:
    """Accept a standalone JSON code fence while rejecting surrounding prose."""
    stripped = response.strip()
    lines = stripped.splitlines()
    if len(lines) >= 3 and lines[0].strip().lower() == "```json" and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1])
    return stripped


def select_proposal(
    state: State, rules: list[dict[str, Any]], perception_answers: dict[str, bool] | None = None
) -> Proposal | None:
    for rule in rules:
        if _matches(state, rule["when"], perception_answers or {}):
            return _proposal_from_rule(state, rule)
    return None


def _rejected(proposal: Proposal, reason: str) -> Outcome:
    return Outcome(False, f"rejected {proposal.label}: {reason}")


def _matches(state: State, condition: dict[str, Any], perception_answers: dict[str, bool]) -> bool:
    if "all" in condition:
        return all(_matches(state, item, perception_answers) for item in condition["all"])
    if "not" in condition:
        return not _matches(state, condition["not"], perception_answers)
    if "perception_answer" in condition:
        expected = condition["perception_answer"]
        return perception_answers.get(expected["question"]) is expected["is"]
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
