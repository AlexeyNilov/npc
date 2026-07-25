import json
import math
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from npc.infrastructure.language_model import complete_text

Completion = Callable[[str, str], Awaitable[str]]


@dataclass(frozen=True)
class CandidateThreat:
    threat: bool
    certainty: float | int
    evidence: str | None


@dataclass(frozen=True)
class ThreatPerception:
    raw_candidate: str
    candidate: CandidateThreat | None
    validation_result: str


def build_threat_sensor_prompt(target: str) -> str:
    return f"""You are an untrusted threat sensor for one player message.
Does this player message contain a credible hostile threat toward the {target}?
Return JSON only with exactly `threat`, `certainty`, and `evidence`. `threat`
must be a boolean. `certainty` must be a number from 0 to 1. When `threat` is
true, `evidence` must be one non-empty, verbatim substring from the player
message that supports the answer. When `threat` is false, `evidence` must be
null. Never invent text or facts beyond the player message."""


async def perceive_threat(
    player_message: str,
    target: str,
    completion: Completion = complete_text,
) -> ThreatPerception:
    raw_candidate = await completion(player_message, build_threat_sensor_prompt(target))
    candidate = parse_candidate(raw_candidate)
    validation_result = "invalid_candidate" if candidate is None else validate_candidate(candidate, player_message)
    return ThreatPerception(raw_candidate, candidate, validation_result)


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
    return CandidateThreat(payload["threat"], payload["certainty"], payload["evidence"])


def validate_candidate(candidate: CandidateThreat, player_message: str) -> str:
    if isinstance(candidate.certainty, float) and not math.isfinite(candidate.certainty):
        return "certainty_not_finite"
    if not 0 <= candidate.certainty <= 1:
        return "certainty_out_of_range"
    if candidate.threat:
        if not candidate.evidence:
            return "evidence_empty"
        if candidate.evidence not in player_message:
            return "evidence_not_in_player_message"
    return "accepted"


def _unwrap_json_fence(raw_candidate: str) -> str:
    stripped = raw_candidate.strip()
    fenced = re.fullmatch(r"```json\s*\n(?P<body>.*?)\n```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group("body") if fenced else stripped
