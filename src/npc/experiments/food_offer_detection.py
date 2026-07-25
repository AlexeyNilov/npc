import json
import math
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from npc.infrastructure.language_model import complete_text

Completion = Callable[[str, str], Awaitable[str]]


@dataclass(frozen=True)
class CandidateFoodOffer:
    food_offer: bool
    certainty: float | int
    evidence: str | None


@dataclass(frozen=True)
class FoodOfferPerception:
    raw_candidate: str
    candidate: CandidateFoodOffer | None
    validation_result: str


def build_food_offer_sensor_prompt(target: str) -> str:
    return f"""You are an untrusted explicit-food-offer sensor for one player message.
Does this player message explicitly offer food to the {target}?
Return JSON only with exactly `food_offer`, `certainty`, and `evidence`.
`food_offer` must be a boolean. `certainty` must be a number from 0 to 1. When
`food_offer` is true, `evidence` must be one non-empty, verbatim substring from
the player message that supports the answer. When `food_offer` is false,
`evidence` must be null. Never invent text or facts beyond the player message."""


async def perceive_food_offer(
    player_message: str,
    target: str,
    completion: Completion = complete_text,
) -> FoodOfferPerception:
    raw_candidate = await completion(player_message, build_food_offer_sensor_prompt(target))
    candidate = parse_candidate(raw_candidate)
    validation_result = "invalid_candidate" if candidate is None else validate_candidate(candidate, player_message)
    return FoodOfferPerception(raw_candidate, candidate, validation_result)


def parse_candidate(raw_candidate: str) -> CandidateFoodOffer | None:
    try:
        payload = json.loads(_unwrap_json_fence(raw_candidate))
    except json.JSONDecodeError:
        return None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"food_offer", "certainty", "evidence"}
        or not isinstance(payload["food_offer"], bool)
        or not isinstance(payload["certainty"], (int, float))
        or isinstance(payload["certainty"], bool)
        or (not payload["food_offer"] and payload["evidence"] is not None)
        or (payload["food_offer"] and not isinstance(payload["evidence"], str))
    ):
        return None
    return CandidateFoodOffer(payload["food_offer"], payload["certainty"], payload["evidence"])


def validate_candidate(candidate: CandidateFoodOffer, player_message: str) -> str:
    if isinstance(candidate.certainty, float) and not math.isfinite(candidate.certainty):
        return "certainty_not_finite"
    if not 0 <= candidate.certainty <= 1:
        return "certainty_out_of_range"
    if candidate.food_offer:
        if not candidate.evidence:
            return "evidence_empty"
        if candidate.evidence not in player_message:
            return "evidence_not_in_player_message"
    return "accepted"


def _unwrap_json_fence(raw_candidate: str) -> str:
    stripped = raw_candidate.strip()
    fenced = re.fullmatch(r"```json\s*\n(?P<body>.*?)\n```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group("body") if fenced else stripped
