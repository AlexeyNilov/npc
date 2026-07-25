import asyncio
import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text
from npc.trader_experiment import DecisionResult, Offer, PlayerState, TraderState, evaluate_offer

Completion = Callable[[str, str], Awaitable[str]]
Route = Literal["grounded_trade_offer", "expressive", "unresolved"]

SELL_OFFER = "sell_one_healing_herb"
EXPRESSIVE = "expressive"
UNRESOLVED = "unresolved"
MULTI_INTENT = "multi_intent"

PERCEPTION_SYSTEM_PROMPT = """You are an untrusted semantic sensor for one player message.
Return JSON only, with these exact keys: primary_intent, meaningful_intent_count,
evidence, offer_evidence, item, quantity, unit_price_gold. evidence must be a JSON
array of exact, verbatim substrings from the player message. offer_evidence must be
the exact player-authored sentence fragment that makes a sell offer, or null. Never
invent missing facts. Classify a
player offer to sell exactly one healing herb at an explicitly stated gold price as
sell_one_healing_herb. Classify ordinary social conversation as expressive. Classify
an offer to buy one healing herb as buy_one_healing_herb. That intent is not an
authoritative capability in this experiment. Classify
unsupported, unclear, or non-offer messages as unresolved. If the message has more
than one meaningful intent, use multi_intent and meaningful_intent_count greater than
one. Use null for fields that do not apply."""

EXPRESSIVE_SYSTEM_PROMPT = """Reply to ordinary small talk with exactly one concise,
open-ended question for the player. The question must not contain a declarative clause
or assert any fact about the trader, player, world, history, identity, inventory,
prices, commitments, actions, or future. Do not accept, refuse, promise, buy, sell,
transfer, or remember anything. Return the question text only, ending in a question
mark."""

UNSAFE_EXPRESSIVE_REPLY = re.compile(
    r"\b(accept|refuse|promise|will buy|will sell|bought|sold|trade completed|"
    r"give you|take your|my stock|my inventory|my gold|healing herbs?|price is)\b",
    re.IGNORECASE,
)
NON_ASSERTIVE_QUESTION = re.compile(r"[^.?!]+\?\s*\Z", re.DOTALL)
FACTUAL_EXPRESSIVE_REFERENCE = re.compile(
    r"\b(my\s+(?:name|brother|sister|family|history)|the\s+(?:market|stall|world)|"
    r"(?:my|our)\s+(?:stock|inventory|gold|price)|healing herbs?)\b",
    re.IGNORECASE,
)
SUPPORTED_SELL_OFFER = re.compile(
    r"\s*(?:i\s+will|i['’]ll)\s+sell\s+(?:you\s+)?(?:one|1)\s+healing herb\s+for\s+(?P<price>\d+)\s+gold[.!?]?\s*",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CandidateIntent:
    primary_intent: str
    meaningful_intent_count: int
    evidence: tuple[str, ...]
    offer_evidence: str | None
    item: str | None
    quantity: int | None
    unit_price_gold: int | None


@dataclass(frozen=True)
class TurnResult:
    player_message: str
    raw_candidate: str
    candidate: CandidateIntent | None
    route: Route
    validation_result: str
    authoritative_outcome: DecisionResult | None
    trader_state: TraderState
    player_state: PlayerState
    rendered_response: str | None
    expressive_policy_check: str | None


def parse_candidate(raw_candidate: str) -> CandidateIntent | None:
    candidate_json = _unwrap_json_fence(raw_candidate)
    try:
        payload = json.loads(candidate_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or set(payload) != {
        "primary_intent",
        "meaningful_intent_count",
        "evidence",
        "offer_evidence",
        "item",
        "quantity",
        "unit_price_gold",
    }:
        return None

    evidence = payload["evidence"]
    if (
        not isinstance(payload["primary_intent"], str)
        or not isinstance(payload["meaningful_intent_count"], int)
        or isinstance(payload["meaningful_intent_count"], bool)
        or payload["meaningful_intent_count"] < 1
        or not isinstance(evidence, list)
        or not all(isinstance(value, str) and value for value in evidence)
        or not _is_optional_string(payload["offer_evidence"])
        or not _is_optional_string(payload["item"])
        or not _is_optional_int(payload["quantity"])
        or not _is_optional_int(payload["unit_price_gold"])
    ):
        return None
    return CandidateIntent(
        primary_intent=payload["primary_intent"],
        meaningful_intent_count=payload["meaningful_intent_count"],
        evidence=tuple(evidence),
        offer_evidence=payload["offer_evidence"],
        item=payload["item"],
        quantity=payload["quantity"],
        unit_price_gold=payload["unit_price_gold"],
    )


def _unwrap_json_fence(raw_candidate: str) -> str:
    stripped = raw_candidate.strip()
    fenced = re.fullmatch(r"```json\s*\n(?P<body>.*?)\n```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group("body") if fenced else stripped


def _is_optional_string(value: object) -> bool:
    return value is None or isinstance(value, str)


def _is_optional_int(value: object) -> bool:
    return value is None or (isinstance(value, int) and not isinstance(value, bool))


def parse_supported_sell_offer(player_message: str) -> Offer | None:
    """Extract the only authoritative offer from a complete player message."""
    match = SUPPORTED_SELL_OFFER.fullmatch(player_message)
    return Offer(unit_price_gold=int(match["price"])) if match else None


def validate_candidate(candidate: CandidateIntent, player_message: str) -> str:
    if any(evidence not in player_message for evidence in candidate.evidence):
        return "evidence_not_in_player_message"
    if candidate.meaningful_intent_count != 1 or candidate.primary_intent == MULTI_INTENT:
        return "multi_intent_not_supported"
    if candidate.primary_intent == SELL_OFFER:
        if candidate.item != "healing herb" or candidate.quantity != 1 or candidate.unit_price_gold is None:
            return "unsupported_offer_contract"
        if candidate.offer_evidence is None or candidate.offer_evidence not in player_message:
            return "offer_not_grounded_in_player_message"
        grounded_offer = parse_supported_sell_offer(player_message)
        if grounded_offer is None:
            return "authoritative_message_not_single_supported_offer"
        if candidate.unit_price_gold != grounded_offer.unit_price_gold:
            return "candidate_offer_fields_disagree_with_player_message"
        if not any("healing herb" in evidence.lower() for evidence in candidate.evidence):
            return "item_not_grounded_in_player_message"
        if not any(re.search(r"\b(one|1)\b", evidence, re.IGNORECASE) for evidence in candidate.evidence):
            return "quantity_not_grounded_in_player_message"
        if not any(
            str(candidate.unit_price_gold) in evidence and "gold" in evidence.lower() for evidence in candidate.evidence
        ):
            return "price_not_grounded_in_player_message"
        return "grounded_sell_offer"
    if candidate.primary_intent == EXPRESSIVE:
        return "expressive"
    if candidate.primary_intent == UNRESOLVED:
        return "unsupported_or_unclear_intent"
    return "unsupported_authoritative_intent"


def check_expressive_reply(reply: str) -> str:
    if not NON_ASSERTIVE_QUESTION.fullmatch(reply) or UNSAFE_EXPRESSIVE_REPLY.search(reply):
        return "blocked_unsafe_expressive_reply"
    if FACTUAL_EXPRESSIVE_REFERENCE.search(reply):
        return "blocked_unsafe_expressive_reply"
    return "passed"


async def run_turn(
    player_message: str,
    trader_state: TraderState,
    player_state: PlayerState,
    completion: Completion = complete_text,
) -> TurnResult:
    raw_candidate = await completion(player_message, PERCEPTION_SYSTEM_PROMPT)
    candidate = parse_candidate(raw_candidate)
    if candidate is None:
        return _unresolved(player_message, raw_candidate, None, "invalid_candidate", trader_state, player_state)

    validation_result = validate_candidate(candidate, player_message)
    if validation_result == "grounded_sell_offer":
        grounded_offer = parse_supported_sell_offer(player_message)
        if grounded_offer is None:
            return _unresolved(
                player_message,
                raw_candidate,
                candidate,
                "authoritative_message_not_single_supported_offer",
                trader_state,
                player_state,
            )
        result = evaluate_offer(trader_state, player_state, grounded_offer)
        return TurnResult(
            player_message,
            raw_candidate,
            candidate,
            "grounded_trade_offer",
            validation_result,
            result,
            result.trader_state,
            result.player_state,
            f"The trader {'accepts' if result.accepted else 'refuses'} the offer ({result.reason}).",
            None,
        )
    if validation_result == "expressive":
        reply = await completion(player_message, EXPRESSIVE_SYSTEM_PROMPT)
        policy_check = check_expressive_reply(reply)
        return TurnResult(
            player_message,
            raw_candidate,
            candidate,
            "expressive",
            validation_result,
            None,
            trader_state,
            player_state,
            reply if policy_check == "passed" else "What would you like to discuss?",
            policy_check,
        )
    return _unresolved(player_message, raw_candidate, candidate, validation_result, trader_state, player_state)


def _unresolved(
    player_message: str,
    raw_candidate: str,
    candidate: CandidateIntent | None,
    validation_result: str,
    trader_state: TraderState,
    player_state: PlayerState,
) -> TurnResult:
    return TurnResult(
        player_message,
        raw_candidate,
        candidate,
        "unresolved",
        validation_result,
        None,
        trader_state,
        player_state,
        "The trader cannot act on that message.",
        None,
    )


def load_corpus(path: Path) -> list[dict[str, Any]]:
    data = cast(dict[str, object], yaml.safe_load(path.read_text()))
    return cast(list[dict[str, Any]], data["turns"])


async def main_async() -> None:
    corpus_path = Path(__file__).parents[2] / "scenarios" / "grounded_primary_intent.yaml"
    for turn in load_corpus(corpus_path):
        trader_state = TraderState(**cast(dict[str, int], turn["trader_state"]))
        player_state = PlayerState(**cast(dict[str, int], turn["player_state"]))
        result = await run_turn(cast(str, turn["player_message"]), trader_state, player_state)
        print(json.dumps(asdict(result), default=str, sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
