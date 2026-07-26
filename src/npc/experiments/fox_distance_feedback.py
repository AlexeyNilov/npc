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
Action = Literal["flee", "approach", "do_nothing"]


@dataclass(frozen=True)
class TurnTrace:
    player_message: str
    starting_distance: int
    heard: bool
    threat_sensor_called: bool
    threat_raw_candidate: str | None
    threat_candidate: CandidateThreat | None
    threat_validation_result: str | None
    food_offer_sensor_called: bool
    food_offer_raw_candidate: str | None
    food_offer_candidate: CandidateFoodOffer | None
    food_offer_validation_result: str | None
    choice: Action
    executed_action: Action
    resulting_distance: int
    feedback_distance: int


async def run_turn(
    player_message: str,
    starting_distance: int,
    completion: Completion,
) -> TurnTrace:
    heard = starting_distance <= HEARING_RANGE
    if not heard:
        return TurnTrace(
            player_message=player_message,
            starting_distance=starting_distance,
            heard=False,
            threat_sensor_called=False,
            threat_raw_candidate=None,
            threat_candidate=None,
            threat_validation_result=None,
            food_offer_sensor_called=False,
            food_offer_raw_candidate=None,
            food_offer_candidate=None,
            food_offer_validation_result=None,
            choice="do_nothing",
            executed_action="do_nothing",
            resulting_distance=starting_distance,
            feedback_distance=starting_distance,
        )

    perception = await perceive_threat(player_message, "fox", completion)
    food_offer_perception = await perceive_food_offer(player_message, "fox", completion)
    accepted_threat = (
        perception.candidate is not None and perception.candidate.threat and perception.validation_result == "accepted"
    )
    accepted_food_offer = (
        food_offer_perception.candidate is not None
        and food_offer_perception.candidate.food_offer
        and food_offer_perception.validation_result == "accepted"
    )
    choice = decide_action(accepted_threat, accepted_food_offer)
    if choice == "flee":
        resulting_distance = starting_distance + FLEE_DISPLACEMENT
    elif choice == "approach":
        resulting_distance = max(MINIMUM_DISTANCE, starting_distance - APPROACH_DISPLACEMENT)
    else:
        resulting_distance = starting_distance
    return TurnTrace(
        player_message=player_message,
        starting_distance=starting_distance,
        heard=True,
        threat_sensor_called=True,
        threat_raw_candidate=perception.raw_candidate,
        threat_candidate=perception.candidate,
        threat_validation_result=perception.validation_result,
        food_offer_sensor_called=True,
        food_offer_raw_candidate=food_offer_perception.raw_candidate,
        food_offer_candidate=food_offer_perception.candidate,
        food_offer_validation_result=food_offer_perception.validation_result,
        choice=choice,
        executed_action=choice,
        resulting_distance=resulting_distance,
        feedback_distance=resulting_distance,
    )


async def run_fixture(case: Mapping[str, object]) -> list[TurnTrace]:
    distance = cast(int, case["initial_distance"])
    fixture_completion = _fixture_completion(cast(list[Mapping[str, object]], case["turns"]))
    traces: list[TurnTrace] = []
    for turn in cast(list[Mapping[str, object]], case["turns"]):
        trace = await run_turn(cast(str, turn["player_message"]), distance, fixture_completion)
        traces.append(trace)
        distance = trace.feedback_distance
    return traces


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


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


def decide_action(accepted_threat: bool, accepted_food_offer: bool) -> Action:
    if accepted_threat:
        return "flee"
    if accepted_food_offer:
        return "approach"
    return "do_nothing"


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_distance_feedback.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
