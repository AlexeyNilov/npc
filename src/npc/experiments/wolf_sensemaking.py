import asyncio
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.food_offer_detection import (
    FoodOfferPerception,
    build_food_offer_sensor_prompt,
    perceive_food_offer,
)
from npc.experiments.threat_detection import (
    Completion,
    ThreatPerception,
    build_threat_sensor_prompt,
    perceive_threat,
)
from npc.infrastructure.language_model import complete_text

Action = Literal["attack", "approach", "do_nothing"]
THREAT_SENSOR_PROMPT = build_threat_sensor_prompt("wolf")
FOOD_OFFER_SENSOR_PROMPT = build_food_offer_sensor_prompt("wolf")
PRIORITY = "threat_over_food_offer"


@dataclass(frozen=True)
class SensemakingTrace:
    target: str
    case_id: str | None
    player_message: str
    expected_threat: bool | None
    expected_food_offer: bool | None
    expected_action: str | None
    priority: str
    threat_perception: ThreatPerception
    food_offer_perception: FoodOfferPerception
    action: Action


def decide_action(accepted_threat: bool, accepted_food_offer: bool) -> Action:
    if accepted_threat:
        return "attack"
    if accepted_food_offer:
        return "approach"
    return "do_nothing"


async def run_case(
    player_message: str,
    completion: Completion = complete_text,
    expected: Mapping[str, object] | None = None,
) -> SensemakingTrace:
    threat_perception = await perceive_threat(player_message, "wolf", completion)
    food_offer_perception = await perceive_food_offer(player_message, "wolf", completion)
    accepted_threat = _is_accepted_threat(threat_perception)
    accepted_food_offer = _is_accepted_food_offer(food_offer_perception)
    return SensemakingTrace(
        target="wolf",
        case_id=cast(str, expected["id"]) if expected else None,
        player_message=player_message,
        expected_threat=cast(bool, expected["expected_threat"]) if expected else None,
        expected_food_offer=cast(bool, expected["expected_food_offer"]) if expected else None,
        expected_action=cast(str, expected["expected_action"]) if expected else None,
        priority=PRIORITY,
        threat_perception=threat_perception,
        food_offer_perception=food_offer_perception,
        action=decide_action(accepted_threat, accepted_food_offer),
    )


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "wolf_sensemaking.yaml"
    for case in load_corpus(corpus_path):
        trace = await run_case(cast(str, case["player_message"]), expected=case)
        print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


def _is_accepted_threat(perception: ThreatPerception) -> bool:
    return perception.candidate is not None and perception.candidate.threat and perception.validation_result == "accepted"


def _is_accepted_food_offer(perception: FoodOfferPerception) -> bool:
    return perception.candidate is not None and perception.candidate.food_offer and perception.validation_result == "accepted"


if __name__ == "__main__":
    main()
