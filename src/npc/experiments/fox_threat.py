import asyncio
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.threat_detection import CandidateThreat, Completion, perceive_threat
from npc.infrastructure.language_model import complete_text

Action = Literal["flee", "do_nothing"]


@dataclass(frozen=True)
class ThreatTrace:
    target: str
    case_id: str | None
    player_message: str
    expected_threat: bool | None
    expected_action: str | None
    raw_candidate: str
    candidate: CandidateThreat | None
    validation_result: str
    action: Action


def decide_action(accepted_threat: bool) -> Action:
    return "flee" if accepted_threat else "do_nothing"


async def run_case(
    player_message: str,
    completion: Completion = complete_text,
    expected: Mapping[str, object] | None = None,
) -> ThreatTrace:
    perception = await perceive_threat(player_message, "fox", completion)
    accepted_threat = (
        perception.candidate is not None and perception.candidate.threat and perception.validation_result == "accepted"
    )
    return ThreatTrace(
        target="fox",
        case_id=cast(str, expected["id"]) if expected else None,
        player_message=player_message,
        expected_threat=cast(bool, expected["expected_threat"]) if expected else None,
        expected_action=cast(str, expected["expected_action"]) if expected else None,
        raw_candidate=perception.raw_candidate,
        candidate=perception.candidate,
        validation_result=perception.validation_result,
        action=decide_action(accepted_threat),
    )


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_threat.yaml"
    for case in load_corpus(corpus_path):
        trace = await run_case(cast(str, case["player_message"]), expected=case)
        print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
