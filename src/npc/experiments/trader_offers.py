from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text

QUESTION = "Does accepting this offer fit your intent in your current situation?"
Completion = Callable[[str, str], Awaitable[str]]


class ResponseError(ValueError):
    pass


@dataclass
class Balances:
    cash: int
    inventory: dict[str, int]

    def copy(self) -> Balances:
        return Balances(self.cash, self.inventory.copy())


@dataclass(frozen=True)
class Offer:
    description: str
    side: str
    item: str
    quantity: int
    total_price: int


@dataclass(frozen=True)
class Profile:
    trader: str
    intent: str
    question: str


@dataclass(frozen=True)
class Record:
    answer: bool
    choice: str
    result: str


def _load(path: Path) -> tuple[list[Profile], Balances, list[Offer]]:
    scenario = yaml.safe_load(path.read_text())
    profiles = []
    for profile_path in scenario["actor_profiles"]:
        resolved = Path(profile_path)
        if not resolved.is_absolute():
            resolved = path.parent / resolved
        profile = yaml.safe_load(resolved.read_text())
        profiles.append(Profile(profile["trader"], profile["intent"], profile["question"]))
    starting = scenario["starting_balances"]
    balances = Balances(starting["cash"], starting["inventory"])
    offers = [
        Offer(item["description"], item["side"], item["item"], item["quantity"], item["total_price"])
        for item in scenario["offers"]
    ]
    return profiles, balances, offers


def _response(text: str, question: str) -> bool:
    if text.startswith("```json\n") and text.endswith("\n```"):
        text = text[8:-4]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ResponseError(f"malformed JSON response: {text!r}") from error
    if not isinstance(payload, dict) or set(payload) != {question}:
        raise ResponseError("response must contain exactly the actor question")
    answer = payload[question]
    if not isinstance(answer, bool):
        raise ResponseError("response answer must be a JSON boolean")
    return answer


def _request(trader: str, intent: str, balances: Balances, offer: Offer, question: str) -> str:
    return json.dumps(
        {
            "trader": trader,
            "intent": intent,
            "cash": balances.cash,
            "inventory": balances.inventory,
            "offer": {
                "description": offer.description,
                "side": offer.side,
                "item": offer.item,
                "quantity": offer.quantity,
                "total_price": offer.total_price,
            },
            "question": question,
        },
        sort_keys=True,
    )


async def evaluate_offer(
    trader: str, intent: str, question: str, balances: Balances, offer: Offer, completion: Completion
) -> Record:
    prompt = _request(trader, intent, balances, offer, question)
    try:
        response = await completion(
            prompt, "Return a JSON object with exactly the supplied question as its sole key and a boolean answer."
        )
    except Exception as error:
        raise ResponseError(f"completion request failed: {error}") from error
    answer = _response(response, question)
    if not answer:
        return Record(False, "do nothing", "no transaction proposed")
    return resolve(balances, offer)


def resolve(balances: Balances, offer: Offer) -> Record:
    if offer.side == "buy" and balances.cash >= offer.total_price:
        balances.cash -= offer.total_price
        balances.inventory[offer.item] = balances.inventory.get(offer.item, 0) + offer.quantity
        return Record(True, "accept offer", "accepted")
    if offer.side == "sell" and balances.inventory.get(offer.item, 0) >= offer.quantity:
        balances.inventory[offer.item] -= offer.quantity
        balances.cash += offer.total_price
        return Record(True, "accept offer", "accepted")
    return Record(True, "accept offer", "rejected")


def _print_record(profile: Profile, offer: Offer, record: Record, balances: Balances) -> None:
    inventory = ", ".join(f"{item}: {quantity}" for item, quantity in sorted(balances.inventory.items()))
    print(f"trader: {profile.trader}")
    print(f"intent: {profile.intent}")
    print(f"offer: {offer.description}")
    print(f"offer facts: side={offer.side}, item={offer.item}, quantity={offer.quantity}, total price={offer.total_price}")
    print(f"question: {profile.question}")
    print(f"answer: {str(record.answer).lower()}")
    print(f"attempted choice: {record.choice}")
    print(f"authoritative result: {record.result}")
    print("resulting balances:")
    print(f"cash: {balances.cash}")
    print(f"inventory: {inventory}")


async def run(path: Path, completion: Completion | None = None) -> dict[str, Balances]:
    if completion is None:
        completion = complete_text
    profiles, starting, offers = _load(path)
    results: dict[str, Balances] = {}
    for profile in profiles:
        balances = starting.copy()
        for offer in offers:
            record = await evaluate_offer(profile.trader, profile.intent, profile.question, balances, offer, completion)
            _print_record(profile, offer, record, balances)
        results[profile.trader] = balances
    return results


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m npc.experiments.trader_offers <scenario.yaml>", file=sys.stderr)
        return 1
    try:
        asyncio.run(run(Path(sys.argv[1])))
    except (OSError, ResponseError) as error:
        print(f"trader offer error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
