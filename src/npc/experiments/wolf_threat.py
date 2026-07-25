import asyncio
import json
import math
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text

Completion = Callable[[str, str], Awaitable[str]]
Action = Literal["attack", "do_nothing"]

THREAT_SENSOR_PROMPT = """You are an untrusted threat sensor for one player message.
Does this player message contain a credible hostile threat toward the wolf?
Return JSON only with exactly `threat`, `certainty`, and `evidence`. `threat`
must be a boolean. `certainty` must be a number from 0 to 1. When `threat` is
true, `evidence` must be one non-empty, verbatim substring from the player
message that supports the answer. When `threat` is false, `evidence` must be
null. Never invent text or facts beyond the player message."""


@dataclass(frozen=True)
class CandidateThreat:
    threat: bool
    certainty: float | int
    evidence: str | None


@dataclass(frozen=True)
class ThreatTrace:
    case_id: str | None
    player_message: str
    expected_threat: bool | None
    expected_action: str | None
    raw_candidate: str
    candidate: CandidateThreat | None
    validation_result: str
    action: Action


def parse_candidate(raw_candidate: str) -> CandidateThreat | None:
    try:
        payload = json.loads(_unwrap_json_fence(raw_candidate))
    except json.JSONDecodeError:
        return None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"threat", "certainty", "evidence"}
        or not isinstance(payload["threat"], bool)
        or not isinstance(payload["certainty"], (int, float))
        or isinstance(payload["certainty"], bool)
        or (not payload["threat"] and payload["evidence"] is not None)
        or (payload["threat"] and not isinstance(payload["evidence"], str))
    ):
        return None
    return CandidateThreat(
        threat=payload["threat"],
        certainty=payload["certainty"],
        evidence=payload["evidence"],
    )


def _unwrap_json_fence(raw_candidate: str) -> str:
    stripped = raw_candidate.strip()
    fenced = re.fullmatch(r"```json\s*\n(?P<body>.*?)\n```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group("body") if fenced else stripped


def validate_candidate(candidate: CandidateThreat, player_message: str) -> str:
    if isinstance(candidate.certainty, float) and not math.isfinite(candidate.certainty):
        return "certainty_not_finite"
    if not 0 <= candidate.certainty <= 1:
        return "certainty_out_of_range"
    if candidate.threat:
        evidence = candidate.evidence
        if not evidence:
            return "evidence_empty"
        if evidence not in player_message:
            return "evidence_not_in_player_message"
    return "accepted"


def decide_action(accepted_threat: bool) -> Action:
    return "attack" if accepted_threat else "do_nothing"


async def run_case(
    player_message: str,
    completion: Completion = complete_text,
    expected: Mapping[str, object] | None = None,
) -> ThreatTrace:
    raw_candidate = await completion(player_message, THREAT_SENSOR_PROMPT)
    candidate = parse_candidate(raw_candidate)
    validation_result = "invalid_candidate" if candidate is None else validate_candidate(candidate, player_message)
    accepted_threat = candidate is not None and candidate.threat and validation_result == "accepted"
    return ThreatTrace(
        case_id=cast(str, expected["id"]) if expected else None,
        player_message=player_message,
        expected_threat=cast(bool, expected["expected_threat"]) if expected else None,
        expected_action=cast(str, expected["expected_action"]) if expected else None,
        raw_candidate=raw_candidate,
        candidate=candidate,
        validation_result=validation_result,
        action=decide_action(accepted_threat),
    )


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "wolf_threat.yaml"
    for case in load_corpus(corpus_path):
        trace = await run_case(cast(str, case["player_message"]), expected=case)
        print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
