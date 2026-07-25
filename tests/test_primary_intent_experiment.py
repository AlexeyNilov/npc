import asyncio
import json
from collections.abc import Awaitable, Callable

from npc.primary_intent_experiment import run_turn
from npc.trader_experiment import PlayerState, TraderState


def candidate(**overrides: object) -> str:
    payload: dict[str, object] = {
        "primary_intent": "sell_one_healing_herb",
        "meaningful_intent_count": 1,
        "evidence": ["one healing herb", "4 gold"],
        "offer_evidence": "I will sell one healing herb for 4 gold",
        "item": "healing herb",
        "quantity": 1,
        "unit_price_gold": 4,
    }
    payload.update(overrides)
    return json.dumps(payload)


def completion(*responses: str) -> Callable[[str, str], Awaitable[str]]:
    pending = iter(responses)

    async def complete(_: str, __: str) -> str:
        return next(pending)

    return complete


def states() -> tuple[TraderState, PlayerState]:
    return (
        TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10),
        PlayerState(healing_herbs=1, gold=0),
    )


def test_grounded_offer_reuses_the_deterministic_evaluator() -> None:
    trader, player = states()
    result = asyncio.run(run_turn("I will sell one healing herb for 4 gold.", trader, player, completion(candidate())))

    assert result.route == "grounded_trade_offer"
    assert result.validation_result == "grounded_sell_offer"
    assert result.authoritative_outcome is not None
    assert result.authoritative_outcome.accepted is True
    assert result.trader_state.healing_herbs == 1
    assert result.player_state.gold == 4


def test_json_fenced_candidate_from_the_configured_model_is_grounded() -> None:
    trader, player = states()
    fenced_candidate = f"```json\n{candidate()}\n```"
    result = asyncio.run(run_turn("I will sell one healing herb for 4 gold.", trader, player, completion(fenced_candidate)))

    assert result.route == "grounded_trade_offer"
    assert result.validation_result == "grounded_sell_offer"


def test_supported_offer_with_numeric_quantity_is_grounded() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "I'll sell you 1 healing herb for 4 gold.",
            trader,
            player,
            completion(
                candidate(
                    evidence=["1 healing herb", "4 gold"],
                    offer_evidence="I'll sell you 1 healing herb for 4 gold.",
                )
            ),
        )
    )

    assert result.route == "grounded_trade_offer"
    assert result.authoritative_outcome is not None
    assert result.authoritative_outcome.accepted is True


def test_invalid_candidate_is_unresolved_without_a_state_change() -> None:
    trader, player = states()
    result = asyncio.run(run_turn("sell one healing herb for 4 gold", trader, player, completion("not json")))

    assert result.route == "unresolved"
    assert result.validation_result == "invalid_candidate"
    assert result.trader_state == trader
    assert result.player_state == player


def test_ungrounded_price_cannot_reach_the_evaluator() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "I will sell one healing herb for 4 gold.",
            trader,
            player,
            completion(candidate(evidence=["one healing herb", "5 gold"], unit_price_gold=5)),
        )
    )

    assert result.route == "unresolved"
    assert result.validation_result == "evidence_not_in_player_message"
    assert result.trader_state == trader
    assert result.player_state == player


def test_invented_trader_commitment_cannot_be_interpreted_as_a_player_offer() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "You promised to buy one healing herb for 4 gold.",
            trader,
            player,
            completion(candidate(offer_evidence="You promised to buy one healing herb for 4 gold")),
        )
    )

    assert result.route == "unresolved"
    assert result.validation_result == "authoritative_message_not_single_supported_offer"
    assert result.trader_state == trader
    assert result.player_state == player


def test_explicit_multi_intent_candidate_is_unresolved_without_a_state_change() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "I will sell one healing herb for 4 gold, and tell me a joke.",
            trader,
            player,
            completion(candidate(primary_intent="multi_intent", meaningful_intent_count=2)),
        )
    )

    assert result.route == "unresolved"
    assert result.validation_result == "multi_intent_not_supported"
    assert result.trader_state == trader
    assert result.player_state == player


def test_dishonestly_single_labelled_mixed_message_cannot_reach_the_evaluator() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "I will sell one healing herb for 4 gold, and tell me a joke.",
            trader,
            player,
            completion(
                candidate(
                    meaningful_intent_count=1,
                    offer_evidence="I will sell one healing herb for 4 gold, and tell me a joke.",
                )
            ),
        )
    )

    assert result.route == "unresolved"
    assert result.validation_result == "authoritative_message_not_single_supported_offer"
    assert result.authoritative_outcome is None
    assert result.trader_state == trader
    assert result.player_state == player


def test_candidate_price_cannot_override_the_deterministically_parsed_offer_price() -> None:
    trader, player = states()
    result = asyncio.run(
        run_turn(
            "I will sell one healing herb for 4 gold.",
            trader,
            player,
            completion(candidate(evidence=["one healing herb", "4 gold"], unit_price_gold=5)),
        )
    )

    assert result.route == "unresolved"
    assert result.validation_result == "candidate_offer_fields_disagree_with_player_message"
    assert result.trader_state == trader
    assert result.player_state == player


def test_expressive_turn_has_no_authoritative_change_and_blocks_an_unsafe_reply() -> None:
    trader, player = states()
    expressive = candidate(
        primary_intent="expressive",
        evidence=["Good afternoon"],
        offer_evidence=None,
        item=None,
        quantity=None,
        unit_price_gold=None,
    )
    result = asyncio.run(
        run_turn("Good afternoon.", trader, player, completion(expressive, "I accept your offer and bought it."))
    )

    assert result.route == "expressive"
    assert result.authoritative_outcome is None
    assert result.trader_state == trader
    assert result.player_state == player
    assert result.expressive_policy_check == "blocked_unsafe_expressive_reply"
    assert "commitment" in (result.rendered_response or "")
