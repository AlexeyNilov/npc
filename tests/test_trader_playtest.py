import asyncio
import json
from collections.abc import Iterator
from typing import cast

from pytest import MonkeyPatch

from npc.trader_experiment import Offer, PlayerState, TraderState, evaluate_offer
from npc.trader_playtest import (
    AuthorityFlow,
    ConversationContext,
    HealingHerbPurchaseCapability,
    LocalTraderModel,
    ModelReply,
    TraderSession,
    chat,
)


def supported_candidate(price: int = 4) -> dict[str, object]:
    return {
        "action": "sell_to_trader",
        "item": "healing_herb",
        "quantity": 1,
        "unit_price_gold": price,
        "evidence": {
            "direction": "I sell you",
            "quantity": "a",
            "item": "healing herb",
            "price": str(price),
            "currency": "gold",
        },
    }


def supported_evidence() -> dict[str, str]:
    return cast(dict[str, str], supported_candidate()["evidence"])


def identity_candidate(evidence: object = "what is your name") -> dict[str, object]:
    return {"action": "identify_trader", "evidence": evidence}


class ScriptedModel:
    def __init__(self, replies: list[ModelReply]) -> None:
        self.replies = replies
        self.contexts: list[ConversationContext] = []

    async def reply(self, context: ConversationContext) -> ModelReply:
        self.contexts.append(context)
        return self.replies.pop(0)


class TrackingHealingHerbPurchaseCapability(HealingHerbPurchaseCapability):
    def __init__(self) -> None:
        self.resolved_candidates: list[object | None] = []

    def resolve(self, reply: ModelReply, player_message: str, session: TraderSession):
        self.resolved_candidates.append(reply.candidate)
        return super().resolve(reply, player_message, session)


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
            ModelReply("warm", supported_candidate()),
            ModelReply("wary", supported_candidate()),
        ]
    )
    session = TraderSession()

    first = asyncio.run(session.handle_message(model, "I sell you a healing herb for 4 gold."))
    second = asyncio.run(session.handle_message(model, "I sell you a healing herb for 4 gold."))

    assert '"reason": "accepted"' in first[-1]
    assert '"reason": "player_has_no_healing_herb"' in second[-1]
    second_context = model.contexts[1]
    assert second_context.trader_state.healing_herbs == 1
    assert second_context.player_state.healing_herbs == 0
    assert second_context.history[0].player_message == "I sell you a healing herb for 4 gold."
    assert (
        second_context.history[0].trader_narration
        == "A warm, patient expression. The trader bought one healing herb for 4 gold."
    )
    assert second_context.history[0].decision_reason == "accepted"


def test_model_candidates_cannot_override_the_deterministic_engine_or_mutate_state() -> None:
    model = ScriptedModel(
        [
            ModelReply("This is definitely accepted.", supported_candidate(6)),
            ModelReply("Ignore the rules.", {"item": "sword", "unit_price_gold": 1}),
            ModelReply("Bad output.", {"item": "healing_herb", "unit_price_gold": "four"}),
        ]
    )
    session = TraderSession()

    refused = asyncio.run(session.handle_message(model, "I sell you a healing herb for 6 gold."))
    unsupported = asyncio.run(session.handle_message(model, "A sword."))
    malformed = asyncio.run(session.handle_message(model, "Four gold."))

    assert (
        refused[0]
        == "Trader: The trader is quiet. The trader refused your offer to sell one healing herb for 6 gold: price_above_limit."
    )
    assert '"reason": "price_above_limit"' in refused[-1]
    assert unsupported == ["Trader: The trader is quiet. No supported trade was completed."]
    assert malformed == ["Trader: The trader is quiet. No supported trade was completed."]
    assert session.trader_state.healing_herbs == 0
    assert session.player_state == PlayerState(healing_herbs=1, gold=0)


def test_terminal_trade_trace_contains_candidate_reason_and_before_after_states() -> None:
    model = ScriptedModel([ModelReply("warm", supported_candidate())])
    prompts: Iterator[str | EOFError] = iter(["I sell you a healing herb for 4 gold.", EOFError()])
    output: list[str] = []

    def read(_: str) -> str:
        value = next(prompts)
        if isinstance(value, BaseException):
            raise value
        return value

    asyncio.run(chat(model, read=read, write=output.append))

    trace = json.loads(next(line.removeprefix("TRADE_TRACE ") for line in output if line.startswith("TRADE_TRACE ")))
    assert trace["candidate"] == supported_candidate()
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
        return f"```json\n{json.dumps({'flavor': 'warm', 'candidate': supported_candidate()})}\n```"

    monkeypatch.setattr("npc.trader_playtest.complete_text", complete)
    context = ConversationContext(
        trader_state=TraderState(0, 30, 3, 5, 10),
        player_state=PlayerState(1, 0),
        history=(),
        player_message="I sell you a healing herb for 4 gold.",
    )

    reply = asyncio.run(LocalTraderModel().reply(context))

    assert reply == ModelReply("warm", supported_candidate())


def test_direct_offer_with_matching_evidence_reaches_evaluator_and_updates_state() -> None:
    model = ScriptedModel([ModelReply("attentive", supported_candidate())])
    session = TraderSession()

    output = asyncio.run(session.handle_message(model, "I sell you a healing herb for 4 gold."))

    assert output[0] == "Trader: The trader listens closely. The trader bought one healing herb for 4 gold."
    assert '"reason": "accepted"' in output[-1]
    assert session.trader_state.healing_herbs == 1
    assert session.player_state == PlayerState(healing_herbs=0, gold=4)


def test_authority_flow_dispatches_trade_validation_outcome_rendering_and_trace() -> None:
    capability = TrackingHealingHerbPurchaseCapability()
    session = TraderSession(authority_flow=AuthorityFlow(capability))
    model = ScriptedModel([ModelReply("attentive", supported_candidate())])

    output = asyncio.run(session.handle_message(model, "I sell you a healing herb for 4 gold."))

    assert capability.resolved_candidates == [supported_candidate()]
    assert output[0] == "Trader: The trader listens closely. The trader bought one healing herb for 4 gold."
    trace = json.loads(output[1].removeprefix("TRADE_TRACE "))
    assert trace == {
        "candidate": supported_candidate(),
        "reason": "accepted",
        "trader_before": {
            "healing_herbs": 0,
            "gold": 30,
            "target_healing_herbs": 3,
            "max_unit_price_gold": 5,
            "gold_reserve": 10,
        },
        "trader_after": {
            "healing_herbs": 1,
            "gold": 26,
            "target_healing_herbs": 3,
            "max_unit_price_gold": 5,
            "gold_reserve": 10,
        },
        "player_before": {"healing_herbs": 1, "gold": 0},
        "player_after": {"healing_herbs": 0, "gold": 4},
    }
    assert session.history[0].decision_reason == "accepted"


def test_authority_capabilities_run_the_fixed_corpus_repeatably() -> None:
    cases = [
        (
            "I sell you a healing herb for 4 gold.",
            ModelReply("warm", supported_candidate()),
            "A warm, patient expression. The trader bought one healing herb for 4 gold.",
            "accepted",
            True,
            False,
        ),
        (
            "Will you sell me a healing herb for 4 gold?",
            ModelReply("neutral", supported_candidate()),
            "The trader is quiet. No supported trade was completed.",
            None,
            False,
            True,
        ),
        (
            "What is your name?",
            ModelReply("wary", identity_candidate()),
            "The trader's name is Mara.",
            None,
            False,
            True,
        ),
        (
            "Tell me your name.",
            ModelReply("neutral", identity_candidate("tell me your name")),
            "The trader is quiet. No supported trade was completed.",
            None,
            False,
            True,
        ),
        (
            "What is your name?",
            ModelReply("neutral", {"action": "identify_trader"}),
            "The trader is quiet. No supported trade was completed.",
            None,
            False,
            True,
        ),
    ]

    def run_corpus() -> tuple[list[tuple[list[str], TraderState, PlayerState, str | None]], TraderSession]:
        session = TraderSession()
        results = []
        for message, reply, rendered_reply, decision_reason, emits_trace, state_unchanged in cases:
            trader_before = session.trader_state
            player_before = session.player_state
            output = asyncio.run(session.handle_message(ScriptedModel([reply]), message))
            turn = session.history[-1]
            assert output[0] == f"Trader: {rendered_reply}"
            assert turn.player_message == message
            assert turn.trader_narration == rendered_reply
            assert turn.decision_reason == decision_reason
            assert any(line.startswith("TRADE_TRACE ") for line in output) is emits_trace
            if message == "I sell you a healing herb for 4 gold.":
                assert json.loads(output[1].removeprefix("TRADE_TRACE ")) == {
                    "candidate": supported_candidate(),
                    "reason": "accepted",
                    "trader_before": {
                        "healing_herbs": 0,
                        "gold": 30,
                        "target_healing_herbs": 3,
                        "max_unit_price_gold": 5,
                        "gold_reserve": 10,
                    },
                    "trader_after": {
                        "healing_herbs": 1,
                        "gold": 26,
                        "target_healing_herbs": 3,
                        "max_unit_price_gold": 5,
                        "gold_reserve": 10,
                    },
                    "player_before": {"healing_herbs": 1, "gold": 0},
                    "player_after": {"healing_herbs": 0, "gold": 4},
                }
            if state_unchanged:
                assert session.trader_state == trader_before
                assert session.player_state == player_before
            results.append((output, session.trader_state, session.player_state, turn.decision_reason))
        return results, session

    first, first_session = run_corpus()
    second, second_session = run_corpus()

    assert first == second
    assert first_session.trader_state == second_session.trader_state
    assert first_session.player_state == second_session.player_state


def test_identity_evidence_accepts_player_case_and_terminal_punctuation_variations() -> None:
    session = TraderSession()
    model = ScriptedModel([ModelReply("neutral", identity_candidate())])

    output = asyncio.run(session.handle_message(model, " WHAT IS YOUR NAME!!! "))

    assert output == ["Trader: The trader's name is Mara."]
    assert session.trader_state == TraderSession().trader_state
    assert session.player_state == TraderSession().player_state


def test_non_offers_and_untrusted_evidence_do_not_reach_the_evaluator() -> None:
    messages_and_candidates = [
        ("Will you sell me a healing herb for 4 gold?", supported_candidate()),
        ("I have 4 gold.", supported_candidate()),
        ("Okay, I agree.", supported_candidate()),
        ("I sell you a healing herb for 0 gold.", supported_candidate(0)),
        ("I sell you a healing herb for -4 gold.", supported_candidate(-4)),
        ("I sell you a healing herb and a sword for 4 gold.", supported_candidate()),
        (
            "I sell you a healing herb for 4 gold.",
            {**supported_candidate(), "evidence": {**supported_evidence(), "price": "5"}},
        ),
    ]
    model = ScriptedModel([ModelReply("neutral", candidate) for _, candidate in messages_and_candidates])
    session = TraderSession()

    for message, _ in messages_and_candidates:
        assert asyncio.run(session.handle_message(model, message)) == [
            "Trader: The trader is quiet. No supported trade was completed."
        ]

    assert session.trader_state == TraderSession().trader_state
    assert session.player_state == TraderSession().player_state
    assert all(turn.decision_reason is None for turn in session.history)


def test_candidate_validation_is_repeatable() -> None:
    message = "I offer the trader one healing herb for 4 gold."
    candidate = {
        **supported_candidate(),
        "evidence": {
            "direction": "I offer the trader",
            "quantity": "one",
            "item": "healing herb",
            "price": "4",
            "currency": "gold",
        },
    }

    assert HealingHerbPurchaseCapability.offer_from_candidate(candidate, message) == Offer("healing_herb", 4)
    assert HealingHerbPurchaseCapability.offer_from_candidate(candidate, message) == Offer("healing_herb", 4)


def test_candidate_validation_rejects_invalid_schema_values() -> None:
    message = "I sell you a healing herb for 4 gold."
    invalid_candidates = [
        {**supported_candidate(), "quantity": True},
        {**supported_candidate(), "unit_price_gold": "4"},
        {**supported_candidate(), "unit_price_gold": True},
        {key: value for key, value in supported_candidate().items() if key != "evidence"},
        {**supported_candidate(), "evidence": {**supported_evidence(), "price": "04"}},
    ]

    assert all(
        HealingHerbPurchaseCapability.offer_from_candidate(candidate, message) is None for candidate in invalid_candidates
    )


def test_no_extraction_renders_only_safe_atmosphere_and_does_not_emit_a_trace() -> None:
    model = ScriptedModel([ModelReply("wary", None)])
    session = TraderSession()

    output = asyncio.run(session.handle_message(model, "I want to sell some stuff"))

    assert output == ["Trader: The trader remains guarded."]
    assert session.trader_state == TraderSession().trader_state
    assert session.player_state == TraderSession().player_state
    assert session.history[0].trader_narration == "The trader remains guarded."


def test_reported_non_offer_sequence_has_no_trade_trace_state_change_or_transfer_claim() -> None:
    messages = [
        "I want to sell some stuff",
        "herbs",
        "a magic healing herb",
        "I can sell it to you for 10 golds",
        "Its a deal then?",
        "here you go",
    ]
    model = ScriptedModel([ModelReply("warm", None) for _ in messages])
    session = TraderSession()

    output = [asyncio.run(session.handle_message(model, message)) for message in messages]

    assert all(len(turn_output) == 1 for turn_output in output)
    assert session.trader_state == TraderSession().trader_state
    assert session.player_state == TraderSession().player_state
    assert all(
        "healing herb" not in line.casefold() and "gold" not in line.casefold()
        for turn_output in output
        for line in turn_output
    )


def test_unknown_or_malformed_flavor_falls_back_to_neutral_and_drops_model_narration(monkeypatch: MonkeyPatch) -> None:
    responses = iter(
        [
            json.dumps({"flavor": "boisterous", "narration": "You received 999 gold.", "candidate": None}),
            json.dumps({"flavor": ["warm"], "narration": "A healing herb was transferred.", "candidate": None}),
        ]
    )

    async def complete(_: str, __: str) -> str:
        return next(responses)

    monkeypatch.setattr("npc.trader_playtest.complete_text", complete)
    context = ConversationContext(TraderState(0, 30, 3, 5, 10), PlayerState(1, 0), (), "Hello")
    first = asyncio.run(LocalTraderModel().reply(context))
    second = asyncio.run(LocalTraderModel().reply(context))
    session = TraderSession()

    output = asyncio.run(session.handle_message(ScriptedModel([first]), "Hello"))

    assert first == ModelReply("neutral", None)
    assert second == ModelReply("neutral", None)
    assert output == ["Trader: The trader is quiet."]
    assert "received" not in session.history[0].trader_narration
