from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text
from npc.platform import LanguageModelMediator, Mediator, Simulation, SimulationBuilder


@dataclass(frozen=True)
class Space:
    kind: str
    name: str | None = None
    price: int | None = None
    rent: int | None = None


@dataclass(frozen=True)
class PropertyBoardConfig:
    spaces: tuple[Space, ...]
    player_ids: tuple[str, ...]
    starting_cash: int
    movement: int
    turn_limit: int


@dataclass(frozen=True)
class PropertyProfile:
    actor_id: str
    intent: str
    questions: tuple[str, ...]
    buy_when_answer: bool


@dataclass(frozen=True)
class PlayerState:
    actor_id: str
    cash: int
    position: int = 0


@dataclass(frozen=True)
class BoardWorld:
    players: tuple[PlayerState, ...]
    owners: tuple[str | None, ...]
    turn: int = 0
    ended: bool = False
    end_reason: str | None = None


@dataclass(frozen=True)
class BuyLandedProperty:
    action: str = "buy_landed_property"


@dataclass(frozen=True)
class BoardOutcome:
    event: str
    landing: int
    ended: bool = False


@dataclass(frozen=True)
class LoadedGame:
    config: PropertyBoardConfig
    profiles: Mapping[str, PropertyProfile]


class AlternatingScheduler:
    def next_participant(self, world: BoardWorld, participants: tuple[str, ...]) -> str | None:
        if world.ended:
            return None
        return participants[world.turn % len(participants)]


class PublicBoardAccess:
    def __init__(self, config: PropertyBoardConfig) -> None:
        self._config = config

    def view_for(self, world: BoardWorld, participant: str, profile: PropertyProfile) -> dict[str, object]:
        landing = _landing_index(world, participant, self._config)
        space = self._config.spaces[landing]
        return {
            "intent": profile.intent,
            "players": [asdict(player) for player in world.players],
            "ownership": list(world.owners),
            "turn": world.turn,
            "turn_limit": self._config.turn_limit,
            "landing": {"index": landing, **_space_facts(space), "owner": world.owners[landing]},
        }


class PurchaseDecisionPolicy:
    def questions_for(self, profile: PropertyProfile, view: dict[str, object]) -> tuple[str, ...]:
        if _is_unowned_property(view):
            return profile.questions
        return ()

    def propose(
        self, profile: PropertyProfile, view: dict[str, object], answers: Mapping[str, bool]
    ) -> BuyLandedProperty | None:
        if not _is_unowned_property(view):
            return None
        if answers.get(profile.questions[0]) is profile.buy_when_answer:
            return BuyLandedProperty()
        return None


class PropertyBoardResolver:
    def __init__(self, config: PropertyBoardConfig) -> None:
        self._config = config

    def resolve(
        self, world: BoardWorld, participant: str, proposal: BuyLandedProperty | None
    ) -> tuple[BoardWorld, BoardOutcome]:
        if participant not in self._config.player_ids:
            raise ValueError(f"unknown property-board participant {participant!r}")
        if proposal is not None and proposal.action != "buy_landed_property":
            raise ValueError("property board accepts only buy_landed_property")

        landing = _landing_index(world, participant, self._config)
        players = list(world.players)
        player_index = self._config.player_ids.index(participant)
        active = players[player_index]
        active = PlayerState(participant, active.cash, landing)
        players[player_index] = active
        owners = list(world.owners)
        space = self._config.spaces[landing]
        event = "landed_neutral"
        ended = False
        end_reason = None

        if space.kind == "property":
            owner = owners[landing]
            if owner is None and proposal is not None:
                assert space.price is not None
                if active.cash >= space.price:
                    active = PlayerState(participant, active.cash - space.price, landing)
                    players[player_index] = active
                    owners[landing] = participant
                    event = "property_bought"
                else:
                    event = "purchase_rejected_insufficient_cash"
            elif owner is not None and owner != participant:
                assert space.rent is not None
                if active.cash < space.rent:
                    event = "unable_to_pay_rent"
                    ended = True
                    end_reason = "unable_to_pay_rent"
                else:
                    owner_index = self._config.player_ids.index(owner)
                    active = PlayerState(participant, active.cash - space.rent, landing)
                    players[player_index] = active
                    owner_state = players[owner_index]
                    players[owner_index] = PlayerState(owner, owner_state.cash + space.rent, owner_state.position)
                    event = "rent_paid"
            elif owner == participant:
                event = "landed_own_property"
            else:
                event = "property_declined"

        next_turn = world.turn + 1
        if not ended and next_turn >= self._config.turn_limit:
            ended = True
            end_reason = "turn_limit_reached"
        next_world = BoardWorld(tuple(players), tuple(owners), next_turn, ended, end_reason)
        return next_world, BoardOutcome(event, landing, ended)


def load_game(path: Path) -> LoadedGame:
    document = _mapping(_yaml(path), str(path))
    platform = _mapping(document.get("platform"), "platform")
    property_board = _mapping(document.get("property_board"), "property_board")
    participant_specs = _list(platform.get("participants"), "platform.participants")
    if platform.get("scheduling") != "alternating":
        raise ValueError("property-board scheduling must be 'alternating'")
    if len(participant_specs) != 2:
        raise ValueError("property board requires exactly two participants")

    profiles: dict[str, PropertyProfile] = {}
    player_ids: list[str] = []
    for specification in participant_specs:
        participant = _mapping(specification, "platform participant")
        actor_id = _string(participant.get("actor_id"), "participant actor_id")
        profile_path = path.parent / _string(participant.get("profile"), "participant profile")
        profile = _load_profile(profile_path)
        if profile.actor_id != actor_id:
            raise ValueError(f"profile {profile_path} actor_id does not match its participant reference")
        if actor_id in profiles:
            raise ValueError("participant actor IDs must be distinct")
        player_ids.append(actor_id)
        profiles[actor_id] = profile

    spaces = tuple(_load_space(item) for item in _list(property_board.get("spaces"), "property_board.spaces"))
    if not 2 <= len(spaces) <= 8 or spaces[0].kind != "start":
        raise ValueError("property board requires two to eight spaces beginning with start")
    if property_board.get("action") != "buy_landed_property":
        raise ValueError("property board action must be buy_landed_property")
    starting_cash = _integer(property_board.get("starting_cash"), "property_board.starting_cash")
    movement = _integer(property_board.get("movement"), "property_board.movement")
    turn_limit = _integer(property_board.get("turn_limit"), "property_board.turn_limit")
    if starting_cash < 0 or movement < 1 or turn_limit < 1:
        raise ValueError("starting cash must be non-negative; movement and turn limit must be positive")
    return LoadedGame(PropertyBoardConfig(spaces, tuple(player_ids), starting_cash, movement, turn_limit), profiles)


def build_game(
    loaded: LoadedGame, mediator: Mediator[dict[str, object]]
) -> Simulation[BoardWorld, PropertyProfile, dict[str, object], BuyLandedProperty | None, BoardOutcome]:
    world = BoardWorld(
        tuple(PlayerState(actor_id, loaded.config.starting_cash) for actor_id in loaded.config.player_ids),
        tuple(None for _ in loaded.config.spaces),
    )
    return SimulationBuilder(
        world=world,
        profiles=loaded.profiles,
        scheduler=AlternatingScheduler(),
        access_policy=PublicBoardAccess(loaded.config),
        decision_policy=PurchaseDecisionPolicy(),
        mediator=mediator,
        resolver=PropertyBoardResolver(loaded.config),
    ).build()


def _landing_index(world: BoardWorld, participant: str, config: PropertyBoardConfig) -> int:
    player = next(player for player in world.players if player.actor_id == participant)
    return (player.position + config.movement) % len(config.spaces)


def _space_facts(space: Space) -> dict[str, object]:
    facts: dict[str, object] = {"kind": space.kind}
    if space.name is not None:
        facts["name"] = space.name
    if space.price is not None:
        facts["price"] = space.price
    if space.rent is not None:
        facts["rent"] = space.rent
    return facts


def _is_unowned_property(view: Mapping[str, object]) -> bool:
    landing = cast(Mapping[str, object], view["landing"])
    return landing["kind"] == "property" and landing["owner"] is None


def _load_profile(path: Path) -> PropertyProfile:
    source = _mapping(_yaml(path), str(path))
    questions = tuple(_string(question, "profile question") for question in _list(source.get("questions"), "profile questions"))
    if len(questions) != 1:
        raise ValueError("a property-board profile requires exactly one binary question")
    return PropertyProfile(
        _string(source.get("actor_id"), "profile actor_id"),
        _string(source.get("intent"), "profile intent"),
        questions,
        _boolean(source.get("buy_when_answer"), "profile buy_when_answer"),
    )


def _load_space(source: object) -> Space:
    value = _mapping(source, "property-board space")
    kind = _string(value.get("kind"), "space kind")
    if kind == "property":
        space = Space(
            kind,
            _string(value.get("name"), "property name"),
            _integer(value.get("price"), "property price"),
            _integer(value.get("rent"), "property rent"),
        )
        assert space.price is not None and space.rent is not None
        if space.price < 1 or space.rent < 1:
            raise ValueError("property price and rent must be positive")
        return space
    if kind in {"start", "neutral"}:
        return Space(kind)
    raise ValueError(f"unknown property-board space kind {kind!r}")


def _yaml(path: Path) -> object:
    with path.open() as source:
        return yaml.safe_load(source)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], value)


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return cast(int, value)


def _boolean(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{name} must be a boolean")
    return cast(bool, value)


async def _run(path: Path) -> None:
    simulation = build_game(load_game(path), LanguageModelMediator(complete_text))
    while (result := await simulation.run_next()) is not None:
        print(json.dumps(asdict(result.record), sort_keys=True))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the two-player property-board application.")
    parser.add_argument("scenario", type=Path, help="path to the property-board scenario YAML")
    args = parser.parse_args(argv)
    asyncio.run(_run(args.scenario))


if __name__ == "__main__":
    main()
