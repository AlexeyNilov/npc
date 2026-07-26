"""One self-contained, replayable autonomous clearing observer session."""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace

from npc.infrastructure.language_model import complete_text

EventSelector = Callable[[], str]
TextCall = Callable[[str], Awaitable[str]]
EVENT_NAMES = ("food_scent", "trap_materials_arrive")


class ClearingError(ValueError):
    """A supplied event or retained clearing record does not satisfy the scenario."""


async def _configured_call(prompt: str) -> str:
    """The scenario's configured real-LLM adapter, kept outside simulation authority."""
    return await complete_text(prompt, "Return a best-effort response. It is non-authoritative presentation only.")


@dataclass(frozen=True)
class ClearingState:
    food_available: bool = False
    trap_materials_available: bool = False
    trap_set: bool = False
    fox_fed: bool = False
    fox_caught: bool = False


@dataclass(frozen=True)
class EventRecord:
    ordinal: int
    name: str
    effect: dict[str, bool]


@dataclass(frozen=True)
class CognitionRecord:
    prompt: str
    raw_output: str | None
    valid: bool
    question: str
    sensemaking: str


@dataclass(frozen=True)
class ActorRecord:
    observation: dict[str, bool]
    retained_context: str
    cognition: CognitionRecord
    proposal: str


@dataclass(frozen=True)
class ResolutionRecord:
    order: tuple[str, str]
    decisions: tuple[str, ...]
    transitions: tuple[str, ...]
    feedback: dict[str, str]


@dataclass(frozen=True)
class NarrationRecord:
    prompt: str
    raw_output: str | None
    valid: bool
    text: str


@dataclass(frozen=True)
class TurnRecord:
    event: EventRecord
    actors: dict[str, ActorRecord]
    resolution: ResolutionRecord
    resulting_state: ClearingState
    ending: str | None
    narration: NarrationRecord


@dataclass(frozen=True)
class SessionRecord:
    turn_limit: int
    initial_state: ClearingState
    turns: tuple[TurnRecord, ...]
    ending: str

    def as_json(self) -> dict[str, object]:
        return asdict(self)

    async def replay(self, candidate: SessionRecord | None = None) -> SessionRecord:
        return await replay(candidate or self)


@dataclass
class _ActiveSession:
    turn_limit: int
    selector: EventSelector
    cognition: TextCall
    narrator: TextCall
    state: ClearingState
    contexts: dict[str, str]
    turns: list[TurnRecord]


def _validate_limit(turn_limit: object) -> int:
    if isinstance(turn_limit, bool) or not isinstance(turn_limit, int) or not 1 <= turn_limit <= 10:
        raise ValueError("turn_limit must be a non-boolean integer from 1 through 10")
    return turn_limit


def _default_selector() -> str:
    return random.choice(EVENT_NAMES)


def _event_effect(name: str) -> dict[str, bool]:
    if name == "food_scent":
        return {"food_available": True, "fox_food_scent": True, "fresh_fox_tracks": True}
    if name == "trap_materials_arrive":
        return {"trap_materials_available": True, "trap_materials_arrive": True}
    raise ClearingError(f"unknown clearing event {name!r}")


def _apply_event(state: ClearingState, effect: Mapping[str, bool]) -> ClearingState:
    return replace(
        state,
        food_available=state.food_available or effect.get("food_available", False),
        trap_materials_available=state.trap_materials_available or effect.get("trap_materials_available", False),
    )


def _observations(state: ClearingState, effect: Mapping[str, bool]) -> dict[str, dict[str, bool]]:
    # These are the complete actor channels. Event names and the other actor's channel never enter them.
    return {
        "fox": {"food_scent": effect.get("fox_food_scent", False)},
        "hunter": {
            "trap_materials_available": state.trap_materials_available,
            "fresh_fox_tracks": effect.get("fresh_fox_tracks", False),
            "trap_set": state.trap_set,
        },
    }


def _cognition_prompt(actor: str, observation: Mapping[str, bool], context: str) -> str:
    facts = json.dumps(dict(observation), sort_keys=True)
    return (
        f"You are the {actor}. Use only this observation: {facts}. Your own prior feedback is: {context!r}. "
        'Return JSON only with nonblank string fields "question" and "sensemaking".'
    )


def _fallback_cognition(actor: str) -> tuple[str, str]:
    return (f"What can the {actor} establish from this turn?", "I will act only on my supplied observation.")


async def _record_cognition(actor: str, observation: dict[str, bool], context: str, call: TextCall) -> CognitionRecord:
    prompt = _cognition_prompt(actor, observation, context)
    raw: str | None
    try:
        raw = await call(prompt)
    except Exception:  # The configured model is presentation-only and may be unavailable.
        raw = None
    try:
        parsed = json.loads(raw) if isinstance(raw, str) and raw.strip() else None
        question = parsed["question"] if isinstance(parsed, dict) else None
        sensemaking = parsed["sensemaking"] if isinstance(parsed, dict) else None
        if not isinstance(question, str) or not question.strip() or not isinstance(sensemaking, str) or not sensemaking.strip():
            raise ValueError
        return CognitionRecord(prompt, raw, True, question, sensemaking)
    except (ValueError, TypeError, json.JSONDecodeError, KeyError):
        question, sensemaking = _fallback_cognition(actor)
        return CognitionRecord(prompt, raw, False, question, sensemaking)


def _proposals(observations: Mapping[str, Mapping[str, bool]]) -> dict[str, str]:
    return {
        "fox": "approach_food" if observations["fox"]["food_scent"] else "wait",
        "hunter": "set_trap"
        if observations["hunter"]["trap_materials_available"] and not observations["hunter"]["trap_set"]
        else "wait",
    }


def _resolve(state: ClearingState, proposals: Mapping[str, str]) -> tuple[ClearingState, ResolutionRecord, str | None]:
    decisions: list[str] = []
    transitions: list[str] = []
    next_state = state
    if proposals["hunter"] == "set_trap" and state.trap_materials_available and not state.trap_set:
        next_state = replace(next_state, trap_set=True)
        decisions.append("trap_set")
        transitions.append("trap_set")
        hunter_feedback = "You set a trap."
    else:
        decisions.append("wait" if proposals["hunter"] == "wait" else "set_trap_rejected")
        hunter_feedback = "You wait." if proposals["hunter"] == "wait" else "You cannot set a trap."
    ending: str | None = None
    if proposals["fox"] == "approach_food" and next_state.trap_set:
        next_state = replace(next_state, fox_caught=True)
        decisions.append("fox_caught")
        transitions.append("fox_caught")
        ending = "caught"
        fox_feedback = "The trap catches you."
    elif proposals["fox"] == "approach_food" and next_state.food_available:
        next_state = replace(next_state, fox_fed=True)
        decisions.append("fox_fed")
        transitions.append("fox_fed")
        ending = "fed"
        fox_feedback = "You reach the food."
    else:
        decisions.append("wait" if proposals["fox"] == "wait" else "approach_food_rejected")
        fox_feedback = "You wait." if proposals["fox"] == "wait" else "You cannot reach food."
    resolution = ResolutionRecord(
        ("hunter", "fox"), tuple(decisions), tuple(transitions), {"hunter": hunter_feedback, "fox": fox_feedback}
    )
    return next_state, resolution, ending


def _narration_prompt(turn: TurnRecord) -> str:
    facts = {
        "event": asdict(turn.event),
        "proposals": {name: actor.proposal for name, actor in turn.actors.items()},
        "resolution": asdict(turn.resolution),
        "state": asdict(turn.resulting_state),
        "ending": turn.ending,
    }
    return "Give one concise, non-authoritative account using only these recorded facts: " + json.dumps(facts, sort_keys=True)


def _fallback_narration(turn: TurnRecord) -> str:
    return (
        f"Turn {turn.event.ordinal}: {turn.event.name}; hunter {turn.actors['hunter'].proposal}, "
        f"fox {turn.actors['fox'].proposal}; decisions: {', '.join(turn.resolution.decisions)}."
    )


async def _record_narration(turn: TurnRecord, call: TextCall) -> NarrationRecord:
    prompt = _narration_prompt(turn)
    try:
        raw = await call(prompt)
    except Exception:
        raw = None
    if isinstance(raw, str) and raw.strip() and not raw.lstrip().startswith(("{", "[")):
        return NarrationRecord(prompt, raw, True, raw.strip())
    return NarrationRecord(prompt, raw, False, _fallback_narration(turn))


async def run_session(
    turn_limit: object,
    *,
    selector: EventSelector | None = None,
    cognition: TextCall = _configured_call,
    narrator: TextCall = _configured_call,
) -> SessionRecord:
    """Run one autonomous session; injection points are for the supplied scenario only."""
    limit = _validate_limit(turn_limit)
    choose = selector or _default_selector
    active = _ActiveSession(limit, choose, cognition, narrator, ClearingState(), {"fox": "", "hunter": ""}, [])
    ending: str | None = None
    while len(active.turns) < limit:
        ending = await _advance(active)
        if ending:
            break
    assert ending is not None
    return SessionRecord(limit, ClearingState(), tuple(active.turns), ending)


async def _advance(active: _ActiveSession) -> str | None:
    ordinal = len(active.turns) + 1
    name = active.selector()
    effect = _event_effect(name)
    event = EventRecord(ordinal, name, dict(effect))
    state_after_event = _apply_event(active.state, effect)
    observations = _observations(state_after_event, effect)
    cognition = {
        actor: ActorRecord(
            dict(observations[actor]),
            active.contexts[actor],
            await _record_cognition(actor, dict(observations[actor]), active.contexts[actor], active.cognition),
            "",
        )
        for actor in ("fox", "hunter")
    }
    proposals = _proposals(observations)
    actors = {actor: replace(record, proposal=proposals[actor]) for actor, record in cognition.items()}
    active.state, resolution, ending = _resolve(state_after_event, proposals)
    if ending is None and ordinal == active.turn_limit:
        ending = "clearing_quiet"
    provisional = TurnRecord(event, actors, resolution, active.state, ending, NarrationRecord("", None, False, ""))
    active.turns.append(replace(provisional, narration=await _record_narration(provisional, active.narrator)))
    active.contexts = dict(resolution.feedback)
    return ending


async def replay(record: SessionRecord) -> SessionRecord:
    """Verify retained history without event selection or LLM cognition/narration calls."""
    _validate_limit(record.turn_limit)
    if record.initial_state != ClearingState() or not record.turns or len(record.turns) > record.turn_limit:
        raise ClearingError("invalid session source record")
    state = record.initial_state
    contexts = {"fox": "", "hunter": ""}
    terminal: str | None = None
    for expected_ordinal, turn in enumerate(record.turns, 1):
        if terminal is not None or turn.event.ordinal != expected_ordinal:
            raise ClearingError("invalid event ordering")
        effect = _event_effect(turn.event.name)
        if turn.event.effect != effect:
            raise ClearingError("event effect does not match selected event")
        state_after_event = _apply_event(state, effect)
        observations = _observations(state_after_event, effect)
        if set(turn.actors) != {"fox", "hunter"}:
            raise ClearingError("invalid actor record")
        proposals = _proposals(observations)
        for actor in ("fox", "hunter"):
            saved = turn.actors[actor]
            if (
                saved.observation != observations[actor]
                or saved.retained_context != contexts[actor]
                or saved.proposal != proposals[actor]
            ):
                raise ClearingError("actor record does not match causal history")
            if not saved.cognition.prompt or not saved.cognition.question or not saved.cognition.sensemaking:
                raise ClearingError("incomplete retained cognition")
        state, resolution, terminal = _resolve(state_after_event, proposals)
        expected_ending = terminal or ("clearing_quiet" if expected_ordinal == record.turn_limit else None)
        expected = TurnRecord(turn.event, turn.actors, resolution, state, expected_ending, turn.narration)
        if turn.resolution != resolution or turn.resulting_state != state or turn.ending != expected_ending:
            raise ClearingError("resolution record does not match causal history")
        if _narration_prompt(expected) != turn.narration.prompt or not turn.narration.text:
            raise ClearingError("invalid retained narration")
        contexts = dict(resolution.feedback)
    expected_ending = terminal or ("clearing_quiet" if len(record.turns) == record.turn_limit else None)
    if expected_ending is None or record.ending != expected_ending or record.turns[-1].ending != expected_ending:
        raise ClearingError("invalid session ending")
    return record


def format_causal_account(turns: Sequence[TurnRecord]) -> str:
    """Render retained clearing facts for observer inspection without model involvement."""
    if not turns:
        return "No completed turns."
    accounts: list[str] = []
    for turn in turns:
        effect = ", ".join(f"{name}={str(value).lower()}" for name, value in sorted(turn.event.effect.items()))
        actor_accounts = []
        for actor in ("fox", "hunter"):
            record = turn.actors[actor]
            actor_accounts.append(
                f"{actor.title()}: question={record.cognition.question}; "
                f"sensemaking={record.cognition.sensemaking}; proposal={record.proposal}"
            )
        feedback = ", ".join(f"{actor}={message}" for actor, message in sorted(turn.resolution.feedback.items()))
        state = ", ".join(f"{name}={str(value).lower()}" for name, value in asdict(turn.resulting_state).items())
        accounts.append(
            f"Turn {turn.event.ordinal}\n"
            f"Event/effect: {turn.event.name}; {effect}\n"
            + "\n".join(actor_accounts)
            + f"\nResolution/feedback: {', '.join(turn.resolution.decisions)}; {feedback}\n"
            f"Resulting state: {state}\n"
            f"Ending: {turn.ending or 'none'}"
        )
    return "\n\n".join(accounts)


def _raw_response(raw_output: str | None) -> str:
    return raw_output if raw_output is not None else "[unavailable]"


def format_turn_presentation(turn: TurnRecord) -> str:
    """Print the completed causal account with its retained, non-authoritative exchanges."""
    exchanges = []
    for actor in ("fox", "hunter"):
        cognition = turn.actors[actor].cognition
        exchanges.append(
            f"{actor.title()} cognition prompt: {cognition.prompt}\nRaw LLM response: {_raw_response(cognition.raw_output)}"
        )
    exchanges.append(f"Narration prompt: {turn.narration.prompt}\nRaw LLM response: {_raw_response(turn.narration.raw_output)}")
    return format_causal_account((turn,)) + "\n" + "\n".join(exchanges)


async def _run_terminal_session(
    turn_limit: int,
    selector: EventSelector,
    cognition: TextCall,
    narrator: TextCall,
    output_fn: Callable[[str], None],
) -> SessionRecord:
    active = _ActiveSession(turn_limit, selector, cognition, narrator, ClearingState(), {"fox": "", "hunter": ""}, [])
    ending: str | None = None
    while ending is None:
        ending = await _advance(active)
        output_fn(format_turn_presentation(active.turns[-1]))
    return SessionRecord(turn_limit, ClearingState(), tuple(active.turns), ending)


def run_terminal(
    turn_limit: int,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    selector: EventSelector | None = None,
    cognition: TextCall = _configured_call,
    narrator: TextCall = _configured_call,
) -> None:
    """Run automatically, then offer only noncausal post-ending observer controls."""
    limit = _validate_limit(turn_limit)
    output_fn("Autonomous clearing: a fox seeks food while a hunter may prepare a trap.")
    choose = selector or _default_selector
    current = asyncio.run(_run_terminal_session(limit, choose, cognition, narrator, output_fn))
    output_fn(f"Session ended: {current.ending}.")
    while True:
        command = input_fn("[inspect, replay, fresh, exit] ").strip().lower()
        if command == "exit":
            return
        if command == "inspect":
            output_fn(format_causal_account(current.turns))
        elif command == "replay":
            asyncio.run(replay(current))
            output_fn("Replay verified exactly.")
        elif command == "fresh":
            current = asyncio.run(_run_terminal_session(limit, choose, cognition, narrator, output_fn))
            output_fn(f"Session ended: {current.ending}.")
        else:
            output_fn("Choose inspect, replay, fresh, or exit.")
