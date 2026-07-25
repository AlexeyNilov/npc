import asyncio

from npc.trader_experiment import PlayerState, TraderState
from npc.trader_playtest import AuthorityOutcome, ModelReply, TraderSession


def supported_purchase_candidate() -> dict[str, object]:
    return {
        "action": "sell_to_trader",
        "item": "healing_herb",
        "quantity": 1,
        "unit_price_gold": 4,
        "evidence": {
            "direction": "I sell you",
            "quantity": "a",
            "item": "healing herb",
            "price": "4",
            "currency": "gold",
        },
    }


def identity_candidate() -> dict[str, object]:
    return {"action": "identify_trader", "evidence": "what is your name"}


class FixedModel:
    def __init__(self, reply: ModelReply) -> None:
        self.reply_value = reply

    async def reply(self, _context: object) -> ModelReply:
        return self.reply_value


def run_fixture(message: str, reply: ModelReply) -> tuple[TraderSession, list[str]]:
    session = TraderSession()
    output = asyncio.run(session.handle_message(FixedModel(reply), message))
    return session, output


def test_same_actor_loop_records_purchase_and_identity_deterministically() -> None:
    purchase_message = "I sell you a healing herb for 4 gold."
    purchase_reply = ModelReply("warm", supported_purchase_candidate())
    identity_message = "What is your name?"
    identity_reply = ModelReply("wary", identity_candidate())

    first_purchase, purchase_output = run_fixture(purchase_message, purchase_reply)
    second_purchase, second_purchase_output = run_fixture(purchase_message, purchase_reply)
    identity, identity_output = run_fixture(identity_message, identity_reply)
    second_identity, second_identity_output = run_fixture(identity_message, identity_reply)

    purchase_record = first_purchase.last_actor_record
    identity_record = identity.last_actor_record
    second_purchase_record = second_purchase.last_actor_record
    second_identity_record = second_identity.last_actor_record
    assert purchase_record is not None
    assert identity_record is not None
    assert isinstance(purchase_record.outcome, AuthorityOutcome)
    assert isinstance(identity_record.outcome, AuthorityOutcome)
    assert second_purchase_record is not None
    assert second_identity_record is not None
    assert tuple(purchase_record.__dataclass_fields__) == (
        "reality",
        "perception",
        "sensemaking",
        "intent",
        "action",
        "outcome",
        "feedback",
    )
    assert type(first_purchase.actor_loop) is type(identity.actor_loop)
    assert purchase_record.outcome.decision_reason == "accepted"
    assert identity_record.outcome.decision_reason is None
    assert purchase_output[-1].startswith("TRADE_TRACE ")
    assert identity_output == ["Trader: The trader's name is Mara."]
    assert identity.trader_state == TraderState(0, 30, 3, 5, 10)
    assert identity.player_state == PlayerState(1, 0)
    assert first_purchase.trader_state == second_purchase.trader_state
    assert first_purchase.player_state == second_purchase.player_state
    assert first_purchase.trader_state.gold + first_purchase.player_state.gold == 30
    assert first_purchase.trader_state.healing_herbs + first_purchase.player_state.healing_herbs == 1
    assert purchase_record.intent == second_purchase_record.intent
    assert purchase_record.outcome == second_purchase_record.outcome
    assert purchase_record.feedback == second_purchase_record.feedback
    assert purchase_output == second_purchase_output
    assert identity.trader_state == second_identity.trader_state
    assert identity.player_state == second_identity.player_state
    assert identity_record.intent == second_identity_record.intent
    assert identity_record.outcome == second_identity_record.outcome
    assert identity_record.feedback == second_identity_record.feedback
    assert identity_output == second_identity_output
