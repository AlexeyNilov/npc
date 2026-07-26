import asyncio
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.food_offer_detection import CandidateFoodOffer, perceive_food_offer
from npc.experiments.threat_detection import CandidateThreat, Completion, perceive_threat

HEARING_RANGE = 10
FLEE_DISPLACEMENT = 5
APPROACH_DISPLACEMENT = 3
MINIMUM_DISTANCE = 1
HUNGER_INCREMENT = 10
MAXIMUM_HUNGER = 100
Action = Literal["flee", "approach", "do_nothing"]
TIE_ORDER: tuple[Action, ...] = ("flee", "approach", "do_nothing")


@dataclass(frozen=True)
class TurnTrace:
    player_message: str
    starting_distance: int
    starting_hunger: int
    heard: bool
    threat_sensor_called: bool
    threat_raw_candidate: str | None
    threat_candidate: CandidateThreat | None
    threat_validation_result: str | None
    food_offer_sensor_called: bool
    food_offer_raw_candidate: str | None
    food_offer_candidate: CandidateFoodOffer | None
    food_offer_validation_result: str | None
    utilities: tuple[tuple[Action, int], ...]
    selected_utility: int
    selection_tie_order: tuple[Action, ...]
    choice: Action
    executed_action: Action
    resulting_distance: int
    feedback_distance: int
    resulting_hunger: int


async def run_turn(
    player_message: str,
    starting_distance: int,
    starting_hunger: int,
    completion: Completion,
) -> TurnTrace:
    _validate_starting_distance(starting_distance)
    _validate_starting_hunger(starting_hunger)

    heard = starting_distance <= HEARING_RANGE
    if not heard:
        return _trace(
            player_message=player_message,
            starting_distance=starting_distance,
            starting_hunger=starting_hunger,
            heard=False,
            threat_sensor_called=False,
            threat_raw_candidate=None,
            threat_candidate=None,
            threat_validation_result=None,
            food_offer_sensor_called=False,
            food_offer_raw_candidate=None,
            food_offer_candidate=None,
            food_offer_validation_result=None,
            accepted_threat=False,
            accepted_food_offer=False,
        )

    threat_perception = await perceive_threat(player_message, "fox", completion)
    food_offer_perception = await perceive_food_offer(player_message, "fox", completion)
    accepted_threat = (
        threat_perception.candidate is not None
        and threat_perception.candidate.threat
        and threat_perception.validation_result == "accepted"
    )
    accepted_food_offer = (
        food_offer_perception.candidate is not None
        and food_offer_perception.candidate.food_offer
        and food_offer_perception.validation_result == "accepted"
    )
    return _trace(
        player_message=player_message,
        starting_distance=starting_distance,
        starting_hunger=starting_hunger,
        heard=True,
        threat_sensor_called=True,
        threat_raw_candidate=threat_perception.raw_candidate,
        threat_candidate=threat_perception.candidate,
        threat_validation_result=threat_perception.validation_result,
        food_offer_sensor_called=True,
        food_offer_raw_candidate=food_offer_perception.raw_candidate,
        food_offer_candidate=food_offer_perception.candidate,
        food_offer_validation_result=food_offer_perception.validation_result,
        accepted_threat=accepted_threat,
        accepted_food_offer=accepted_food_offer,
    )


async def run_fixture(case: Mapping[str, object]) -> list[TurnTrace]:
    distance = cast(int, case["initial_distance"])
    hunger = cast(int, case["initial_hunger"])
    turns = cast(list[Mapping[str, object]], case["turns"])
    fixture_completion = _fixture_completion(turns)
    traces: list[TurnTrace] = []
    for turn in turns:
        trace = await run_turn(cast(str, turn["player_message"]), distance, hunger, fixture_completion)
        traces.append(trace)
        distance = trace.feedback_distance
        hunger = trace.resulting_hunger
    return traces


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


def _trace(
    *,
    player_message: str,
    starting_distance: int,
    starting_hunger: int,
    heard: bool,
    threat_sensor_called: bool,
    threat_raw_candidate: str | None,
    threat_candidate: CandidateThreat | None,
    threat_validation_result: str | None,
    food_offer_sensor_called: bool,
    food_offer_raw_candidate: str | None,
    food_offer_candidate: CandidateFoodOffer | None,
    food_offer_validation_result: str | None,
    accepted_threat: bool,
    accepted_food_offer: bool,
) -> TurnTrace:
    utilities: tuple[tuple[Action, int], ...] = (
        ("flee", 60 if accepted_threat else 0),
        ("approach", starting_hunger if accepted_food_offer else 0),
        ("do_nothing", 1),
    )
    choice: Action = "do_nothing"
    selected_utility = -1
    for action, utility in utilities:
        if utility > selected_utility:
            choice = action
            selected_utility = utility
    if choice == "flee":
        resulting_distance = starting_distance + FLEE_DISPLACEMENT
    elif choice == "approach":
        resulting_distance = max(MINIMUM_DISTANCE, starting_distance - APPROACH_DISPLACEMENT)
    else:
        resulting_distance = starting_distance
    return TurnTrace(
        player_message=player_message,
        starting_distance=starting_distance,
        starting_hunger=starting_hunger,
        heard=heard,
        threat_sensor_called=threat_sensor_called,
        threat_raw_candidate=threat_raw_candidate,
        threat_candidate=threat_candidate,
        threat_validation_result=threat_validation_result,
        food_offer_sensor_called=food_offer_sensor_called,
        food_offer_raw_candidate=food_offer_raw_candidate,
        food_offer_candidate=food_offer_candidate,
        food_offer_validation_result=food_offer_validation_result,
        utilities=utilities,
        selected_utility=selected_utility,
        selection_tie_order=TIE_ORDER,
        choice=choice,
        executed_action=choice,
        resulting_distance=resulting_distance,
        feedback_distance=resulting_distance,
        resulting_hunger=min(MAXIMUM_HUNGER, starting_hunger + HUNGER_INCREMENT),
    )


def _validate_starting_distance(starting_distance: object) -> None:
    if isinstance(starting_distance, bool) or not isinstance(starting_distance, int) or starting_distance < MINIMUM_DISTANCE:
        raise ValueError("starting_distance must be a non-boolean integer greater than or equal to 1")


def _validate_starting_hunger(starting_hunger: object) -> None:
    if isinstance(starting_hunger, bool) or not isinstance(starting_hunger, int) or not 0 <= starting_hunger <= MAXIMUM_HUNGER:
        raise ValueError("starting_hunger must be a non-boolean integer from 0 through 100")


def _fixture_completion(turns: list[Mapping[str, object]]) -> Completion:
    responses = iter(
        cast(
            list[str],
            [
                response
                for turn in turns
                for response in (turn.get("threat_completion"), turn.get("food_offer_completion"))
                if response is not None
            ],
        )
    )

    async def complete(_: str, __: str) -> str:
        return next(responses)

    return complete


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_deterministic_utility.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
