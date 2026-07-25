import asyncio
import json
from collections.abc import Iterator

from pytest import MonkeyPatch

from npc.trader_experiment import Offer, PlayerState, TraderState, evaluate_offer
from npc.trader_playtest import ConversationContext, LocalTraderModel, ModelReply, TraderSession, chat


class ScriptedModel:
    def __init__(self, replies: list[ModelReply]) -> None:
        self.replies = replies
        self.contexts: list[ConversationContext] = []

    async def reply(self, context: ConversationContext) -> ModelReply:
        self.contexts.append(context)
        return self.replies.pop(0)


def test_refuses_a_sale_when_the_player_has_no_healing_herb() -> None:
    trader = TraderState(healing_herbs=1, gold=26, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    player = PlayerState(healing_herbs=0, gold=4)

    result = evaluate_offer(trader, player, Offer(name="healing_herb", unit_price_gold=4))

    assert result.accepted is False
    assert result.reason == "player_has_no_healing_herb"
    assert result.trader_state == trader
    assert result.player_state == player


def test_session_uses_updated_state_and_history_for_a_follow_up_offer() -> None:
    model = ScriptedModel(
        [
            ModelReply("I can buy that.", {"item": "healing_herb", "unit_price_gold": 4}),
            ModelReply("I cannot buy another.", {"item": "healing_herb", "unit_price_gold": 4}),
        ]
    )
    session = TraderSession()

    first = asyncio.run(session.handle_message(model, "I will sell you a herb for four gold."))
    second = asyncio.run(session.handle_message(model, "How about another for four gold?"))

    assert '"reason": "accepted"' in first[-1]
    assert '"reason": "player_has_no_healing_herb"' in second[-1]
    second_context = model.contexts[1]
    assert second_context.trader_state.healing_herbs == 1
    assert second_context.player_state.healing_herbs == 0
    assert second_context.history[0].player_message == "I will sell you a herb for four gold."
    assert second_context.history[0].decision_reason == "accepted"


def test_model_candidates_cannot_override_the_deterministic_engine_or_mutate_state() -> None:
    model = ScriptedModel(
        [
            ModelReply("This is definitely accepted.", {"item": "healing_herb", "unit_price_gold": 6}),
            ModelReply("Ignore the rules.", {"item": "sword", "unit_price_gold": 1}),
            ModelReply("Bad output.", {"item": "healing_herb", "unit_price_gold": "four"}),
        ]
    )
    session = TraderSession()

    refused = asyncio.run(session.handle_message(model, "Six gold."))
    unsupported = asyncio.run(session.handle_message(model, "A sword."))
    malformed = asyncio.run(session.handle_message(model, "Four gold."))

    assert '"reason": "price_above_limit"' in refused[-1]
    assert unsupported == ["Trader: Ignore the rules."]
    assert malformed == ["Trader: Bad output."]
    assert session.trader_state.healing_herbs == 0
    assert session.player_state == PlayerState(healing_herbs=1, gold=0)


def test_terminal_trade_trace_contains_candidate_reason_and_before_after_states() -> None:
    model = ScriptedModel([ModelReply("A deal.", {"item": "healing_herb", "unit_price_gold": 4})])
    prompts: Iterator[str | EOFError] = iter(["I will sell a herb for four gold.", EOFError()])
    output: list[str] = []

    def read(_: str) -> str:
        value = next(prompts)
        if isinstance(value, BaseException):
            raise value
        return value

    asyncio.run(chat(model, read=read, write=output.append))

    trace = json.loads(next(line.removeprefix("TRADE_TRACE ") for line in output if line.startswith("TRADE_TRACE ")))
    assert trace["candidate"] == {"item": "healing_herb", "unit_price_gold": 4}
    assert trace["reason"] == "accepted"
    assert trace["trader_before"]["healing_herbs"] == 0
    assert trace["trader_after"]["healing_herbs"] == 1
    assert trace["player_before"]["healing_herbs"] == 1
    assert trace["player_after"]["healing_herbs"] == 0


def test_terminal_exit_command_ends_without_calling_the_model() -> None:
    model = ScriptedModel([])
    output: list[str] = []

    asyncio.run(chat(model, read=lambda _: "/exit", write=output.append))

    assert output[-1] == "Bye."
    assert model.contexts == []


def test_local_model_accepts_a_json_response_wrapped_in_a_markdown_fence(monkeypatch: MonkeyPatch) -> None:
    async def complete(_: str, __: str) -> str:
        return '```json\n{"narration": "A deal.", "candidate": {"item": "healing_herb", "unit_price_gold": 4}}\n```'

    monkeypatch.setattr("npc.trader_playtest.complete_text", complete)
    context = ConversationContext(
        trader_state=TraderState(0, 30, 3, 5, 10),
        player_state=PlayerState(1, 0),
        history=(),
        player_message="Four gold.",
    )

    reply = asyncio.run(LocalTraderModel().reply(context))

    assert reply == ModelReply("A deal.", {"item": "healing_herb", "unit_price_gold": 4})
