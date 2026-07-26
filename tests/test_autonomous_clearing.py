import asyncio
import json
from dataclasses import replace
from typing import cast

import pytest

from npc.experiments.autonomous_clearing import (
    ClearingError,
    SessionRecord,
    TurnRecord,
    format_causal_account,
    run_session,
    run_terminal,
)


async def no_llm(_: str) -> str:
    return '{"question": "What changed?", "sensemaking": "I will respond to what I can see."}'


async def no_narrator(_: str) -> str:
    return "A recorded turn concludes."


def selector(*events: str):
    selected = iter(events)

    def choose() -> str:
        return next(selected)

    return choose


def test_turn_limit_validates_before_any_causal_or_actor_work() -> None:
    calls: list[str] = []

    def selected() -> str:
        calls.append("selector")
        return "food_scent"

    for invalid in (True, False, 0, 11, 1.0, "1", None):
        with pytest.raises(ValueError):
            asyncio.run(run_session(invalid, selector=selected, cognition=no_llm, narrator=no_narrator))
    assert calls == []


def test_event_histories_control_outcomes_and_are_json_safe_by_value() -> None:
    fed = asyncio.run(run_session(3, selector=selector("food_scent"), cognition=no_llm, narrator=no_narrator))
    caught = asyncio.run(
        run_session(3, selector=selector("trap_materials_arrive", "food_scent"), cognition=no_llm, narrator=no_narrator)
    )
    quiet = asyncio.run(
        run_session(
            3,
            selector=selector("trap_materials_arrive", "trap_materials_arrive", "trap_materials_arrive"),
            cognition=no_llm,
            narrator=no_narrator,
        )
    )

    assert fed.ending == "fed"
    assert caught.ending == "caught"
    assert quiet.ending == "clearing_quiet"
    assert asyncio.run(quiet.replay()) == quiet
    assert [turn.event.name for turn in quiet.turns] == ["trap_materials_arrive"] * 3
    assert quiet.turns[1].event.ordinal == 2
    assert quiet.turns[0].resolution.order == ("hunter", "fox")
    assert '"ending": "clearing_quiet"' in quiet.turns[-1].narration.prompt
    assert "trap_materials_available" not in quiet.turns[0].actors["fox"].observation
    assert "food_available" not in quiet.turns[0].actors["hunter"].observation
    json.dumps(quiet.as_json(), sort_keys=True)


@pytest.mark.parametrize("kind", ("blank", "malformed", "unavailable", "exceptional"))
def test_cognition_and_narration_fallbacks_leave_authority_unchanged(kind: str) -> None:
    async def broken(_: str) -> str:
        return "{malformed"

    async def blank(_: str) -> str:
        return ""

    async def unavailable(_: str) -> str:
        return cast(str, None)

    async def exceptional(_: str) -> str:
        raise OSError("LLM unavailable")

    call = {"blank": blank, "malformed": broken, "unavailable": unavailable, "exceptional": exceptional}[kind]
    session = asyncio.run(run_session(1, selector=selector("food_scent"), cognition=call, narrator=call))
    fox = session.turns[0].actors["fox"].cognition
    assert fox.valid is False
    assert session.turns[0].actors["fox"].proposal == "approach_food"
    assert session.turns[0].narration.valid is False
    assert session.ending == "fed"


def test_replay_uses_retained_history_and_rejects_changed_authority() -> None:
    calls: list[str] = []

    events = iter(("trap_materials_arrive", "food_scent"))

    def selected() -> str:
        calls.append("selector")
        return next(events)

    async def cognition(_: str) -> str:
        calls.append("cognition")
        return await no_llm("")

    async def narration(_: str) -> str:
        calls.append("narration")
        return await no_narrator("")

    session = asyncio.run(run_session(2, selector=selected, cognition=cognition, narrator=narration))
    calls_before_replay = list(calls)
    assert asyncio.run(session.replay()) == session
    assert calls == calls_before_replay

    first, second = session.turns
    actor = first.actors["fox"]
    mutations = (
        replace(session, turn_limit=1),
        replace(session, turns=(first,)),
        replace(session, turns=(second, first)),
        replace(session, turns=(replace(first, event=replace(first.event, ordinal=2)), second)),
        replace(session, turns=(replace(first, event=replace(first.event, name="food_scent")), second)),
        replace(first, event=replace(first.event, effect={"food_available": True})),
        replace(first, actors={**first.actors, "fox": replace(actor, observation={"food_scent": True})}),
        replace(first, actors={**first.actors, "fox": replace(actor, retained_context="changed")}),
        replace(first, actors={**first.actors, "fox": replace(actor, proposal="approach_food")}),
        replace(first, resolution=replace(first.resolution, decisions=("changed", "wait"))),
        replace(first, resolution=replace(first.resolution, feedback={"fox": "changed", "hunter": "wait"})),
        replace(first, resulting_state=replace(first.resulting_state, fox_fed=True)),
        replace(first, ending="caught"),
    )
    for index, mutation in enumerate(mutations):
        candidate = (
            mutation if isinstance(mutation, SessionRecord) else replace(session, turns=(cast(TurnRecord, mutation), second))
        )
        try:
            asyncio.run(session.replay(candidate))
        except ClearingError:
            continue
        raise AssertionError(f"mutation {index} was accepted")
    assert calls == calls_before_replay


def test_terminal_controls_are_noncausal_and_resume_one_pending_turn() -> None:
    commands = iter(("start", "inspect", "pause", "resume", "inspect", "replay", "fresh", "exit"))
    output: list[str] = []

    run_terminal(
        1,
        input_fn=lambda _: next(commands),
        output_fn=output.append,
        selector=selector("food_scent", "trap_materials_arrive"),
        cognition=no_llm,
        narrator=no_narrator,
    )

    assert output[1] == "Session started and paused before its next turn."
    assert output[2] == "No completed turns."
    assert output[3] == "Paused between completed turns."
    assert output[4] == "A recorded turn concludes."
    assert "food_scent" in output[6]
    assert output[7] == "Replay verified exactly."
    assert output[8] == "Session started and paused before its next turn."


def test_terminal_pauses_after_a_nonterminal_turn_and_fresh_discards_its_history() -> None:
    commands = iter(("start", "resume", "pause", "inspect", "fresh", "inspect", "resume", "exit"))
    output: list[str] = []

    run_terminal(
        2,
        input_fn=lambda _: next(commands),
        output_fn=output.append,
        selector=selector("trap_materials_arrive", "food_scent", "food_scent"),
        cognition=no_llm,
        narrator=no_narrator,
    )

    account = output[4]
    assert output[3] == "Paused between completed turns."
    assert "Turn 1" in account
    assert "Event/effect: trap_materials_arrive" in account
    assert "Fox: question=" in account and "sensemaking=" in account and "proposal=wait" in account
    assert "Hunter: question=" in account and "proposal=set_trap" in account
    assert "Resolution/feedback:" in account and "Resulting state:" in account and "Ending: none" in account
    assert output[5] == "Session started and paused before its next turn."
    assert output[6] == "No completed turns."
    assert output[7] == "A recorded turn concludes."
    assert output[8] == "Session ended: fed."


def test_causal_formatter_uses_only_retained_turn_facts() -> None:
    session = asyncio.run(run_session(1, selector=selector("food_scent"), cognition=no_llm, narrator=no_narrator))

    account = format_causal_account(session.turns)

    assert "Event/effect: food_scent" in account
    assert "Ending: fed" in account
