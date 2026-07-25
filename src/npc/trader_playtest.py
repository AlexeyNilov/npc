import asyncio
import json
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol

from npc.actor_loop import ActorLoop, ActorLoopRecord, ActorLoopResult
from npc.infrastructure.language_model import complete_text
from npc.trader_experiment import Offer, PlayerState, TraderState, evaluate_offer

INITIAL_TRADER_STATE = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
INITIAL_PLAYER_STATE = PlayerState(healing_herbs=1, gold=0)

SYSTEM_PROMPT = """You are a trader in a small playtest. Reply with JSON only:
{
  "flavor": "warm",
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
Flavor must be exactly one of warm, neutral, attentive, or wary. It supplies
only atmosphere and cannot describe an item, price, balance, transfer,
acceptance, refusal, promise, or completed action.
For a request whose complete player message is what is your name, candidate may
instead be {"action": "identify_trader", "evidence": "what is your name"}.
Otherwise, set candidate to null unless the player explicitly offers to sell
exactly one healing herb for a positive decimal-integer gold price. Trade
evidence values must be exact excerpts from the player message. Direction must
include I before sell or offer and then you or the trader. Quantity and item
must be the contiguous phrase one, 1, or a followed by healing herb. Price and
currency must be the contiguous phrase for <positive decimal digits> gold. The
candidate is only a proposal; do not claim that a trade was accepted or refused."""

_DIRECTION = re.compile(r"I\b.*\b(?:sell|offer)\b.*\b(?:you|the\s+trader)\b", re.IGNORECASE)
_PRICE = re.compile(r"[1-9][0-9]*")
_ADDITIONAL_ITEM = re.compile(r"\b(?:and|,)\s+(?:one|1|a)\s+[a-z]+", re.IGNORECASE)
_FLAVOR_TEXT = {
    "warm": "A warm, patient expression.",
    "neutral": "The trader is quiet.",
    "attentive": "The trader listens closely.",
    "wary": "The trader remains guarded.",
}


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
    flavor: str
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
            return ModelReply("neutral", None)
        if not isinstance(data, dict):
            return ModelReply("neutral", None)
        flavor = data.get("flavor")
        if not isinstance(flavor, str) or flavor not in _FLAVOR_TEXT:
            flavor = "neutral"
        return ModelReply(flavor, data.get("candidate"))


@dataclass(frozen=True)
class AuthorityOutcome:
    rendered_reply: str
    decision_reason: str | None
    trace_payload: dict[str, object] | None
    trader_state: TraderState
    player_state: PlayerState


@dataclass(frozen=True)
class TraderReality:
    trader_state: TraderState
    player_state: PlayerState
    player_message: str


@dataclass(frozen=True)
class UnsupportedPerception:
    flavor: str
    has_candidate: bool


@dataclass(frozen=True)
class TradePerception:
    flavor: str
    candidate: object
    offer: Offer


@dataclass(frozen=True)
class IdentityPerception:
    flavor: str


TraderPerception = UnsupportedPerception | TradePerception | IdentityPerception


def _has_candidate(perception: TraderPerception) -> bool:
    return not isinstance(perception, UnsupportedPerception) or perception.has_candidate


@dataclass(frozen=True)
class TraderIntent:
    name: str = "resolve_validated_perception"


@dataclass(frozen=True)
class AuthorityAction:
    perception: TraderPerception


class TraderStateContext(Protocol):
    @property
    def trader_state(self) -> TraderState: ...

    @property
    def player_state(self) -> PlayerState: ...


class AuthorityCapability(Protocol):
    def resolve(self, perception: TraderPerception, session: TraderStateContext) -> AuthorityOutcome: ...


class HealingHerbPurchaseCapability:
    def resolve(self, perception: TraderPerception, session: TraderStateContext) -> AuthorityOutcome:
        if not isinstance(perception, TradePerception):
            return AuthorityOutcome(
                self.render(perception.flavor, _has_candidate(perception), None, None),
                None,
                None,
                session.trader_state,
                session.player_state,
            )

        trader_before = session.trader_state
        player_before = session.player_state
        result = evaluate_offer(trader_before, player_before, perception.offer)
        return AuthorityOutcome(
            self.render(perception.flavor, True, perception.offer, result.reason),
            result.reason,
            {
                "candidate": perception.candidate,
                "reason": result.reason,
                "trader_before": asdict(trader_before),
                "trader_after": asdict(result.trader_state),
                "player_before": asdict(player_before),
                "player_after": asdict(result.player_state),
            },
            result.trader_state,
            result.player_state,
        )

    @staticmethod
    def render(flavor: str, has_candidate: bool, offer: Offer | None, decision_reason: str | None) -> str:
        atmosphere = _FLAVOR_TEXT.get(flavor, _FLAVOR_TEXT["neutral"])
        if offer is None:
            return atmosphere if not has_candidate else f"{atmosphere} No supported trade was completed."
        if decision_reason == "accepted":
            return f"{atmosphere} The trader bought one healing herb for {offer.unit_price_gold} gold."
        return (
            f"{atmosphere} The trader refused your offer to sell one healing herb for "
            f"{offer.unit_price_gold} gold: {decision_reason}."
        )

    @staticmethod
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


class TraderIdentityCapability:
    _NAME = "Mara"
    _ACTION = "identify_trader"
    _SUPPORTED_MESSAGE = "what is your name"

    def resolve(self, perception: TraderPerception, session: TraderStateContext) -> AuthorityOutcome:
        if isinstance(perception, IdentityPerception):
            return AuthorityOutcome(
                f"The trader's name is {self._NAME}.", None, None, session.trader_state, session.player_state
            )
        return AuthorityOutcome(
            HealingHerbPurchaseCapability.render(perception.flavor, _has_candidate(perception), None, None),
            None,
            None,
            session.trader_state,
            session.player_state,
        )

    @classmethod
    def _is_supported(cls, candidate: object, player_message: str) -> bool:
        if not isinstance(candidate, dict):
            return False
        evidence = candidate.get("evidence")
        return (
            set(candidate) == {"action", "evidence"}
            and candidate.get("action") == cls._ACTION
            and isinstance(evidence, str)
            and evidence == cls._normalized_player_message(player_message)
            and evidence == cls._SUPPORTED_MESSAGE
        )

    @staticmethod
    def _normalized_player_message(player_message: str) -> str:
        return player_message.casefold().strip().rstrip(".?!").strip()


class TraderCapabilityDispatch:
    def __init__(self) -> None:
        self.identity = TraderIdentityCapability()
        self.purchase = HealingHerbPurchaseCapability()

    def resolve(self, perception: TraderPerception, session: TraderStateContext) -> AuthorityOutcome:
        if isinstance(perception, IdentityPerception):
            return self.identity.resolve(perception, session)
        return self.purchase.resolve(perception, session)


class AuthorityFlow:
    def __init__(self, capability: AuthorityCapability) -> None:
        self.capability = capability

    def perceive(self, reality: object, model_output: object) -> object:
        assert isinstance(reality, TraderReality)
        assert isinstance(model_output, ModelReply)
        flavor = model_output.flavor if model_output.flavor in _FLAVOR_TEXT else "neutral"
        if TraderIdentityCapability._is_supported(model_output.candidate, reality.player_message):
            return IdentityPerception(flavor)
        offer = HealingHerbPurchaseCapability.offer_from_candidate(model_output.candidate, reality.player_message)
        if offer is not None:
            return TradePerception(flavor, model_output.candidate, offer)
        return UnsupportedPerception(flavor, model_output.candidate is not None)

    def sensemake(self, reality: object, perception: object) -> object:
        return perception

    def intend(self, reality: object, sensemaking: object) -> object:
        assert isinstance(sensemaking, (UnsupportedPerception, TradePerception, IdentityPerception))
        return TraderIntent()

    def act(self, reality: object, sensemaking: object, intent: object) -> object:
        assert isinstance(sensemaking, (UnsupportedPerception, TradePerception, IdentityPerception))
        assert isinstance(intent, TraderIntent)
        return AuthorityAction(sensemaking)

    def resolve(self, reality: object, action: object) -> tuple[object, object]:
        assert isinstance(reality, TraderReality)
        assert isinstance(action, AuthorityAction)
        outcome = self.capability.resolve(action.perception, reality)
        return outcome, TraderReality(outcome.trader_state, outcome.player_state, reality.player_message)

    def feedback(self, reality: object, outcome: object) -> object:
        assert isinstance(outcome, AuthorityOutcome)
        return outcome

    def run(self, loop: ActorLoop, reality: TraderReality, reply: ModelReply) -> ActorLoopResult:
        return loop.run(reality, reply, self)


class TraderSession:
    def __init__(self, authority_flow: AuthorityFlow | None = None) -> None:
        self.trader_state = INITIAL_TRADER_STATE
        self.player_state = INITIAL_PLAYER_STATE
        self.history: list[ConversationTurn] = []
        self.authority_flow = authority_flow or AuthorityFlow(TraderCapabilityDispatch())
        self.actor_loop = ActorLoop()
        self.last_actor_record: ActorLoopRecord | None = None

    async def handle_message(self, model: TraderModel, player_message: str) -> list[str]:
        context = ConversationContext(
            trader_state=self.trader_state,
            player_state=self.player_state,
            history=tuple(self.history),
            player_message=player_message,
        )
        reply = await model.reply(context)
        result = self.authority_flow.run(
            self.actor_loop,
            TraderReality(self.trader_state, self.player_state, player_message),
            reply,
        )
        outcome = result.record.outcome
        assert isinstance(outcome, AuthorityOutcome)
        self.trader_state = outcome.trader_state
        self.player_state = outcome.player_state
        self.last_actor_record = result.record
        output = [f"Trader: {outcome.rendered_reply}"]
        if outcome.trace_payload is not None:
            output.append("TRADE_TRACE " + json.dumps(outcome.trace_payload, sort_keys=True))
        self.history.append(ConversationTurn(player_message, outcome.rendered_reply, reply.candidate, outcome.decision_reason))
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
