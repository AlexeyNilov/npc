#!/usr/bin/env python3
"""Chat interactively with the configured local LLM.

Run from the repository root after installing the project:
    python sample/chat.py
"""

import argparse
import asyncio
from collections.abc import Sequence

from local_llm_project_template.infrastructure.language_model import stream_text


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


async def chat(system_prompt: str) -> None:
    """Read prompts from stdin and stream each response to stdout."""
    print("Local LLM chat. Type /exit (or press Ctrl-D) to quit.")

    while True:
        try:
            prompt = input("\nYou: ").strip()
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print("\nBye.")
            return

        if prompt in {"/exit", "/quit"}:
            print("Bye.")
            return
        if not prompt:
            continue

        print("Assistant: ", end="", flush=True)
        try:
            async for text in stream_text(prompt, system_prompt):
                print(text, end="", flush=True)
        except Exception as error:
            print(f"\nRequest failed: {error}")
        else:
            print()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat with the configured local LLM.")
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="Instructions sent with every message.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(chat(args.system_prompt))


if __name__ == "__main__":
    main()
