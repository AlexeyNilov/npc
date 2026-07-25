#!/usr/bin/env python3
"""Talk interactively with the grounded-primary-intent trader experiment.

Run from the repository root after installing the project:
    python sample/trader_chat.py
"""

import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import asdict

from npc.infrastructure.language_model import complete_text, stream_text
from npc.primary_intent_experiment import (
    EXPRESSIVE_SYSTEM_PROMPT,
    PERCEPTION_SYSTEM_PROMPT,
    check_expressive_reply,
    parse_candidate,
    parse_supported_sell_offer,
    validate_candidate,
)
from npc.trader_experiment import PlayerState, TraderState, evaluate_offer


async def stream_reply(player_message: str) -> tuple[str, str]:
    """Receive an expressive reply through the streaming client before displaying it.

    The response is buffered so the experiment's policy check can block it before
    it reaches the terminal.
    """
    chunks: list[str] = []
    async for chunk in stream_text(player_message, EXPRESSIVE_SYSTEM_PROMPT):
        chunks.append(chunk)
    reply = "".join(chunks)
    return reply, check_expressive_reply(reply)


def show_state(trader_state: TraderState, player_state: PlayerState) -> None:
    print(
        "State: "
        f"trader(healing_herbs={trader_state.healing_herbs}, gold={trader_state.gold}); "
        f"player(healing_herbs={player_state.healing_herbs}, gold={player_state.gold})"
    )


async def chat(trader_state: TraderState, player_state: PlayerState) -> None:
    """Run independent perception and expressive-output requests for each turn."""
    print("Trader experiment. Type /state to inspect state; /exit (or Ctrl-D) to quit.")
    show_state(trader_state, player_state)

    while True:
        try:
            player_message = input("\nYou: ").strip()
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print("\nBye.")
            return

        if player_message in {"/exit", "/quit"}:
            print("Bye.")
            return
        if player_message == "/state":
            show_state(trader_state, player_state)
            continue
        if not player_message:
            continue

        try:
            raw_candidate = await complete_text(player_message, PERCEPTION_SYSTEM_PROMPT)
        except Exception as error:
            print(f"Perception request failed: {error}")
            continue

        candidate = parse_candidate(raw_candidate)
        if candidate is None:
            print("Trace: route=unresolved validation=invalid_candidate")
            print("Trader: The trader cannot act on that message.")
            continue

        validation_result = validate_candidate(candidate, player_message)
        trace = json.dumps(asdict(candidate), sort_keys=True)
        print(f"Trace: candidate={trace}; validation={validation_result}")

        if validation_result == "grounded_sell_offer":
            grounded_offer = parse_supported_sell_offer(player_message)
            if grounded_offer is None:
                print("Trader: The trader cannot act on that message.")
                continue
            result = evaluate_offer(trader_state, player_state, grounded_offer)
            trader_state, player_state = result.trader_state, result.player_state
            print(f"Trader: The trader {'accepts' if result.accepted else 'refuses'} the offer ({result.reason}).")
            show_state(trader_state, player_state)
            continue

        if validation_result != "expressive":
            print("Trader: The trader cannot act on that message.")
            continue

        try:
            reply, policy_check = await stream_reply(player_message)
        except Exception as error:
            print(f"Expressive reply failed: {error}")
            continue

        if policy_check == "passed":
            print(f"Trader: {reply}")
        else:
            print("Trader: The trader acknowledges you without making a commitment.")
        print(f"Trace: route=expressive expressive_policy_check={policy_check}")
        show_state(trader_state, player_state)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Talk with the grounded trader experiment.")
    parser.add_argument("--trader-healing-herbs", type=int, default=0)
    parser.add_argument("--trader-gold", type=int, default=30)
    parser.add_argument("--target-healing-herbs", type=int, default=3)
    parser.add_argument("--max-unit-price-gold", type=int, default=5)
    parser.add_argument("--gold-reserve", type=int, default=10)
    parser.add_argument("--player-healing-herbs", type=int, default=1)
    parser.add_argument("--player-gold", type=int, default=0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    trader_state = TraderState(
        healing_herbs=args.trader_healing_herbs,
        gold=args.trader_gold,
        target_healing_herbs=args.target_healing_herbs,
        max_unit_price_gold=args.max_unit_price_gold,
        gold_reserve=args.gold_reserve,
    )
    player_state = PlayerState(healing_herbs=args.player_healing_herbs, gold=args.player_gold)
    asyncio.run(chat(trader_state, player_state))


if __name__ == "__main__":
    main()
