#!/usr/bin/env python3
"""Interact with the deterministic fox turn loop from a terminal.

Run from the repository root after installing the project:
    python sample/fox_chat.py
"""

import argparse
import asyncio
from collections.abc import Sequence

from npc.experiments.fox_distance_feedback import TurnTrace, run_turn
from npc.experiments.fox_outcome_rendering import Renderer, RenderingTrace, configured_narrator, render_completed_turn
from npc.experiments.threat_detection import Completion
from npc.infrastructure.language_model import complete_text


async def chat_turn(
    player_message: str,
    starting_distance: int,
    completion: Completion = complete_text,
    narrator: Renderer = configured_narrator,
) -> RenderingTrace:
    """Complete one authoritative fox turn, then render its non-authoritative outcome."""
    canonical_turn: TurnTrace = await run_turn(player_message, starting_distance, completion)
    return await render_completed_turn(canonical_turn, narrator)


async def chat(
    starting_distance: int,
    completion: Completion = complete_text,
    narrator: Renderer = configured_narrator,
) -> None:
    """Read independent player turns and carry only authoritative distance forward."""
    distance = starting_distance
    print("Fox turn chat. Type /exit (or press Ctrl-D) to quit.")

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
        if not player_message:
            continue

        trace = await chat_turn(player_message, distance, completion, narrator)
        distance = trace.canonical_turn.feedback_distance
        print(f"Fox: {trace.rendered_text}")
        print(f"Distance: {distance}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic fox turns with non-authoritative narration.")
    parser.add_argument("--starting-distance", type=int, default=10, help="Initial authoritative distance from the fox.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(chat(args.starting_distance))


if __name__ == "__main__":
    main()
