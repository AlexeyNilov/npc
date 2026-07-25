import asyncio
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol

from npc.infrastructure.language_model import complete_text
from npc.trader_experiment import Offer, PlayerState, TraderState, evaluate_offer

INITIAL_TRADER_STATE = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
INITIAL_PLAYER_STATE = PlayerState(healing_herbs=1, gold=0)

SYSTEM_PROMPT = """You are a trader in a small playtest. Reply with JSON only:
{"narration": "brief response", "candidate": {"item": "healing_herb", "unit_price_gold": 4}}
Set candidate to null unless the player is offering to sell exactly one healing herb for an integer gold price.
The candidate is only a proposal; do not claim that a trade was accepted or refused."""


@dataclass(frozen=True)
class ConversationTurn:
    player_message: str
    trader_narration: str
    candidate: object | None
    decision_reason: str | None


@dataclass(frozen=True)
class ConversationContext:
    trader_state: TraderState
    player_state: PlayerState
    history: tuple[ConversationTurn, ...]
    player_message: str


@dataclass(frozen=True)
class ModelReply:
    narration: str
    candidate: object | None


class TraderModel(Protocol):
    async def reply(self, context: ConversationContext) -> ModelReply: ...


class LocalTraderModel:
    async def reply(self, context: ConversationContext) -> ModelReply:
        prompt = json.dumps(
            {
                "trader_state": asdict(context.trader_state),
                "player_state": asdict(context.player_state),
                "history": [asdict(turn) for turn in context.history],
                "player_message": context.player_message,
            }
        )
        response = await complete_text(prompt, SYSTEM_PROMPT)
        if response.startswith("```json") and response.endswith("```"):
            response = response.removeprefix("```json").removesuffix("```").strip()
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return ModelReply(response, None)
        if not isinstance(data, dict) or not isinstance(data.get("narration"), str):
            return ModelReply(response, None)
        return ModelReply(data["narration"], data.get("candidate"))


def offer_from_candidate(candidate: object) -> Offer | None:
    if not isinstance(candidate, dict):
        return None
    item = candidate.get("item")
    price = candidate.get("unit_price_gold")
    if item != "healing_herb" or not isinstance(price, int) or isinstance(price, bool):
        return None
    return Offer(name="healing_herb", unit_price_gold=price)


class TraderSession:
    def __init__(self) -> None:
        self.trader_state = INITIAL_TRADER_STATE
        self.player_state = INITIAL_PLAYER_STATE
        self.history: list[ConversationTurn] = []

    async def handle_message(self, model: TraderModel, player_message: str) -> list[str]:
        context = ConversationContext(
            trader_state=self.trader_state,
            player_state=self.player_state,
            history=tuple(self.history),
            player_message=player_message,
        )
        reply = await model.reply(context)
        output = [f"Trader: {reply.narration}"]
        offer = offer_from_candidate(reply.candidate)
        decision_reason = None
        if offer is not None:
            trader_before = self.trader_state
            player_before = self.player_state
            result = evaluate_offer(trader_before, player_before, offer)
            self.trader_state = result.trader_state
            self.player_state = result.player_state
            decision_reason = result.reason
            output.append(
                "TRADE_TRACE "
                + json.dumps(
                    {
                        "candidate": reply.candidate,
                        "reason": result.reason,
                        "trader_before": asdict(trader_before),
                        "trader_after": asdict(result.trader_state),
                        "player_before": asdict(player_before),
                        "player_after": asdict(result.player_state),
                    },
                    sort_keys=True,
                )
            )
        self.history.append(ConversationTurn(player_message, reply.narration, reply.candidate, decision_reason))
        return output


async def chat(
    model: TraderModel,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> None:
    session = TraderSession()
    write("Trader playtest. Type /exit or press Ctrl-D to quit.")
    while True:
        try:
            message = read("You: ").strip()
        except EOFError:
            write("")
            return
        except KeyboardInterrupt:
            write("\nBye.")
            return
        if message == "/exit":
            write("Bye.")
            return
        if message:
            for line in await session.handle_message(model, message):
                write(line)


def main() -> None:
    asyncio.run(chat(LocalTraderModel()))


if __name__ == "__main__":
    main()
