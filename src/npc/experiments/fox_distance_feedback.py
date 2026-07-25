import asyncio
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.fox_threat import decide_action
from npc.experiments.threat_detection import CandidateThreat, Completion, perceive_threat

HEARING_RANGE = 10
FLEE_DISPLACEMENT = 5
Action = Literal["flee", "do_nothing"]


@dataclass(frozen=True)
class TurnTrace:
    player_message: str
    starting_distance: int
    heard: bool
    sensor_called: bool
    raw_candidate: str | None
    candidate: CandidateThreat | None
    validation_result: str | None
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
            sensor_called=False,
            raw_candidate=None,
            candidate=None,
            validation_result=None,
            choice="do_nothing",
            executed_action="do_nothing",
            resulting_distance=starting_distance,
            feedback_distance=starting_distance,
        )

    perception = await perceive_threat(player_message, "fox", completion)
    accepted_threat = (
        perception.candidate is not None and perception.candidate.threat and perception.validation_result == "accepted"
    )
    choice = decide_action(accepted_threat)
    resulting_distance = starting_distance + FLEE_DISPLACEMENT if choice == "flee" else starting_distance
    return TurnTrace(
        player_message=player_message,
        starting_distance=starting_distance,
        heard=True,
        sensor_called=True,
        raw_candidate=perception.raw_candidate,
        candidate=perception.candidate,
        validation_result=perception.validation_result,
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
    responses = iter(cast(list[str], [turn["completion"] for turn in turns if turn.get("completion") is not None]))

    async def complete(_: str, __: str) -> str:
        return next(responses)

    return complete


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_distance_feedback.yaml"
    for case in load_corpus(corpus_path):
        for trace in await run_fixture(case):
            print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
