from __future__ import annotations

import asyncio
from collections.abc import Mapping
from pathlib import Path

import pytest

from npc.platform import MediationError
from npc.property_board import (
    BoardWorld,
    PlayerState,
    PropertyBoardResolver,
    PublicBoardAccess,
    build_game,
    load_game,
    render_turn,
)

SCENARIO = Path("scenarios/property_board.yaml")


class Answers:
    def __init__(self, answers: list[Mapping[str, bool]]) -> None:
        self._answers = iter(answers)
        self.calls: list[tuple[dict[str, object], tuple[str, ...]]] = []

    async def answer(self, view: dict[str, object], questions: tuple[str, ...]) -> Mapping[str, bool]:
        self.calls.append((view, questions))
        return next(self._answers) if questions else {}


class RejectAllAnswers:
    async def answer(self, view: dict[str, object], questions: tuple[str, ...]) -> Mapping[str, bool]:
        return {question: False for question in questions}


def test_yaml_fixture_composes_separate_profiles_and_shared_public_facts() -> None:
    loaded = load_game(SCENARIO)
    collector = loaded.profiles["collector"]
    conserver = loaded.profiles["conserver"]
    world = BoardWorld(
        tuple(PlayerState(actor_id, loaded.config.starting_cash) for actor_id in loaded.config.player_ids),
        tuple(None for _ in loaded.config.spaces),
    )

    collector_view = PublicBoardAccess(loaded.config).view_for(world, "collector", collector)
    conserver_view = PublicBoardAccess(loaded.config).view_for(world, "conserver", conserver)

    assert tuple((space.price, space.rent) for space in loaded.config.spaces if space.kind == "property") == (
        (2, 1),
        (3, 1),
        (4, 2),
        (5, 2),
        (6, 3),
        (7, 3),
    )
    assert loaded.config.player_ids == ("collector", "conserver")
    assert (
        loaded.config.starting_cash,
        loaded.config.movement_minimum,
        loaded.config.movement_maximum,
        loaded.config.turn_limit,
    ) == (
        12,
        1,
        3,
        16,
    )
    assert collector.intent != conserver.intent
    assert collector.questions != conserver.questions
    assert collector_view["intent"] == collector.intent
    assert conserver_view["intent"] == conserver.intent
    assert {key: value for key, value in collector_view.items() if key != "intent"} == {
        key: value for key, value in conserver_view.items() if key != "intent"
    }


def test_profiles_make_distinct_recorded_buy_decisions_from_the_same_landing() -> None:
    loaded = load_game(SCENARIO)
    collector_question = loaded.profiles["collector"].questions[0]
    conserver_question = loaded.profiles["conserver"].questions[0]
    answers = Answers([{collector_question: False}, {conserver_question: True}])
    simulation = build_game(loaded, answers, movement_seed=6)

    first = asyncio.run(simulation.run_next())
    second = asyncio.run(simulation.run_next())

    assert first is not None and second is not None
    assert first.record.proposal is None
    assert first.record.outcome.event == "property_declined"
    assert second.record.proposal is not None
    assert second.record.proposal.action == "buy_landed_property"
    assert second.record.outcome.event == "property_bought"
    assert first.record.answers == ((collector_question, False),)
    assert second.record.answers == ((conserver_question, True),)
    assert simulation.world.owners[1] == "conserver"
    assert render_turn(second.record, simulation.world) == (
        "Turn 2/16 — conserver (rolled 1)\n"
        "Landed on amber (price 2; rent 1).\n"
        "Decision: Should I buy this landed property without endangering my cash reserve? yes.\n"
        "Action: buy landed property.\n"
        "Outcome: bought amber for 2.\n"
        "Cash: collector 12 | conserver 10"
    )


def test_resolver_collects_rent_and_ends_immediately_when_it_cannot_be_paid() -> None:
    loaded = load_game(SCENARIO)
    resolver = PropertyBoardResolver(loaded.config)
    owners = (None, "collector", None, None, None, None, None, None)
    world = BoardWorld((PlayerState("collector", 10), PlayerState("conserver", 12)), owners, movement_seed=6)

    after_rent, rent_outcome = resolver.resolve(world, "conserver", None)
    unable_world = BoardWorld((PlayerState("collector", 10), PlayerState("conserver", 0)), owners, movement_seed=6)
    after_failure, failure_outcome = resolver.resolve(unable_world, "conserver", None)

    assert rent_outcome.event == "rent_paid"
    assert after_rent.players == (PlayerState("collector", 11), PlayerState("conserver", 11, 1))
    assert failure_outcome.event == "unable_to_pay_rent"
    assert failure_outcome.ended is True
    assert after_failure.ended is True
    assert after_failure.end_reason == "unable_to_pay_rent"


def test_resolver_ends_on_the_sixteenth_completed_turn() -> None:
    loaded = load_game(SCENARIO)
    resolver = PropertyBoardResolver(loaded.config)
    world = BoardWorld(
        (PlayerState("collector", 12), PlayerState("conserver", 12)),
        tuple(None for _ in loaded.config.spaces),
        turn=15,
    )

    after, outcome = resolver.resolve(world, "conserver", None)

    assert after.turn == 16
    assert after.ended is True
    assert after.end_reason == "turn_limit_reached"
    assert outcome.ended is True


def test_composed_game_stops_after_sixteen_turns() -> None:
    loaded = load_game(SCENARIO)
    simulation = build_game(loaded, RejectAllAnswers(), movement_seed=6)

    results = []
    while (result := asyncio.run(simulation.run_next())) is not None:
        results.append(result)

    assert len(results) == 16
    assert simulation.world.ended is True
    assert simulation.world.end_reason == "turn_limit_reached"
    assert len(simulation.history) == 16


def test_seeded_movement_is_replayable_and_varies_between_seeds() -> None:
    loaded = load_game(SCENARIO)
    world = BoardWorld(
        (PlayerState("collector", 12), PlayerState("conserver", 12)),
        tuple(None for _ in loaded.config.spaces),
        movement_seed=6,
    )
    other_world = BoardWorld(world.players, world.owners, movement_seed=7)
    access = PublicBoardAccess(loaded.config)

    first = access.view_for(world, "collector", loaded.profiles["collector"])
    replay = access.view_for(world, "collector", loaded.profiles["collector"])
    other = access.view_for(other_world, "collector", loaded.profiles["collector"])

    assert first["movement"] == replay["movement"] == 1
    assert other["movement"] in {1, 2, 3}
    assert (first["movement"], first["landing"]) != (other["movement"], other["landing"])


def test_invalid_mediation_cannot_move_or_resolve_the_board() -> None:
    loaded = load_game(SCENARIO)
    question = loaded.profiles["collector"].questions[0]
    simulation = build_game(loaded, Answers([{question: "yes"}]))  # type: ignore[dict-item]

    with pytest.raises(MediationError, match="JSON booleans"):
        asyncio.run(simulation.run_next())

    assert simulation.world.turn == 0
    assert simulation.history == ()
