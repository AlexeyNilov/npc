import asyncio
import json
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol

from npc.infrastructure.language_model import complete_text
from npc.trader_experiment import Offer, PlayerState, TraderState, evaluate_offer

INITIAL_TRADER_STATE = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
INITIAL_PLAYER_STATE = PlayerState(healing_herbs=1, gold=0)

SYSTEM_PROMPT = """You are a trader in a small playtest. Reply with JSON only:
{
  "narration": "brief response",
  "candidate": {
    "action": "sell_to_trader",
    "item": "healing_herb",
    "quantity": 1,
    "unit_price_gold": 4,
    "evidence": {
      "direction": "I sell you",
      "quantity": "a",
      "item": "healing herb",
      "price": "4",
      "currency": "gold"
    }
  }
}
Set candidate to null unless the player explicitly offers to sell exactly one
healing herb for a positive decimal-integer gold price. Evidence values must be
exact excerpts from the player message. Direction must include I before sell or
offer and then you or the trader. Quantity and item must be the contiguous
phrase one, 1, or a followed by healing herb. Price and currency must be the
contiguous phrase for <positive decimal digits> gold.
The candidate is only a proposal; do not claim that a trade was accepted or refused."""

_DIRECTION = re.compile(r"I\b.*\b(?:sell|offer)\b.*\b(?:you|the\s+trader)\b", re.IGNORECASE)
_PRICE = re.compile(r"[1-9][0-9]*")
_ADDITIONAL_ITEM = re.compile(r"\b(?:and|,)\s+(?:one|1|a)\s+[a-z]+", re.IGNORECASE)


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


def offer_from_candidate(candidate: object, player_message: str) -> Offer | None:
    if not isinstance(candidate, dict):
        return None
    action = candidate.get("action")
    item = candidate.get("item")
    quantity = candidate.get("quantity")
    price = candidate.get("unit_price_gold")
    evidence = candidate.get("evidence")
    if (
        action != "sell_to_trader"
        or item != "healing_herb"
        or quantity != 1
        or isinstance(quantity, bool)
        or not isinstance(price, int)
        or isinstance(price, bool)
        or not isinstance(evidence, dict)
    ):
        return None
    direction = evidence.get("direction")
    evidence_quantity = evidence.get("quantity")
    evidence_item = evidence.get("item")
    evidence_price = evidence.get("price")
    currency = evidence.get("currency")
    if (
        not isinstance(direction, str)
        or not isinstance(evidence_quantity, str)
        or not isinstance(evidence_item, str)
        or not isinstance(evidence_price, str)
        or not isinstance(currency, str)
    ):
        return None
    if (
        _DIRECTION.fullmatch(direction) is None
        or evidence_quantity.casefold() not in {"one", "1", "a"}
        or evidence_item.casefold() != "healing herb"
        or _PRICE.fullmatch(evidence_price) is None
        or int(evidence_price) != price
        or currency.casefold() != "gold"
    ):
        return None
    direction_end = player_message.casefold().find(direction.casefold())
    if direction_end < 0:
        return None
    direction_end += len(direction)
    quantity_item = f"{evidence_quantity} {evidence_item}"
    quantity_end = player_message.casefold().find(quantity_item.casefold(), direction_end)
    if quantity_end < 0:
        return None
    quantity_end += len(quantity_item)
    price_currency = f"for {evidence_price} {currency}"
    price_start = player_message.casefold().find(price_currency.casefold(), quantity_end)
    if price_start < 0 or _ADDITIONAL_ITEM.search(player_message[quantity_end:price_start]) is not None:
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
        offer = offer_from_candidate(reply.candidate, player_message)
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
