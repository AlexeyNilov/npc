#!/usr/bin/env python3
"""Interact with the deterministic fox turn loop from a terminal.

Run from the repository root after installing the project:
    python sample/fox_chat.py
"""

import argparse
import asyncio
from collections.abc import Sequence
from dataclasses import dataclass

from npc.experiments.fox_deterministic_utility import TurnTrace, run_turn
from npc.experiments.fox_outcome_rendering import Renderer, RenderingTrace, configured_narrator, render_completed_turn
from npc.experiments.threat_detection import Completion
from npc.infrastructure.language_model import complete_text


@dataclass(frozen=True)
class ChatTrace:
    canonical_turn: TurnTrace
    prompt: str
    rendered_text: str
    non_authoritative: bool


async def chat_turn(
    player_message: str,
    starting_distance: int,
    starting_hunger: int,
    completion: Completion = complete_text,
    narrator: Renderer = configured_narrator,
) -> ChatTrace:
    """Complete one authoritative fox turn, then render its non-authoritative outcome."""
    canonical_turn: TurnTrace = await run_turn(player_message, starting_distance, starting_hunger, completion)
    rendering: RenderingTrace = await render_completed_turn(canonical_turn, narrator)
    return ChatTrace(
        canonical_turn=canonical_turn,
        prompt=rendering.prompt,
        rendered_text=rendering.rendered_text,
        non_authoritative=rendering.non_authoritative,
    )


async def chat(
    starting_distance: int,
    starting_hunger: int,
    completion: Completion = complete_text,
    narrator: Renderer = configured_narrator,
) -> None:
    """Read independent player turns and carry authoritative distance and hunger forward."""
    distance = starting_distance
    hunger = starting_hunger
    print(f"Fox utility chat. Starting distance: {distance}; hunger: {hunger}. Type /exit (or press Ctrl-D) to quit.")

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

        trace = await chat_turn(player_message, distance, hunger, completion, narrator)
        distance = trace.canonical_turn.feedback_distance
        hunger = trace.canonical_turn.resulting_hunger
        utilities = ", ".join(f"{action}={utility}" for action, utility in trace.canonical_turn.utilities)
        print(
            f"Action: {trace.canonical_turn.executed_action} ({trace.canonical_turn.selected_utility}); utilities: {utilities}"
        )
        print(f"Narration (non-authoritative): {trace.rendered_text}")
        print(f"Distance: {distance}; hunger: {hunger}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic fox turns with non-authoritative narration.")
    parser.add_argument("--starting-distance", type=int, default=10, help="Initial authoritative distance from the fox.")
    parser.add_argument("--starting-hunger", type=int, default=50, help="Initial authoritative fox hunger from 0 through 100.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(chat(args.starting_distance, args.starting_hunger))


if __name__ == "__main__":
    main()
