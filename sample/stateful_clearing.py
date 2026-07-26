#!/usr/bin/env python3
"""Run and replay the supplied two-step clearing declaration.

Run from the repository root:
    PYTHONPATH=src .venv/bin/python sample/stateful_clearing.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence

from npc.composition import replay_timeline, run_timeline
from npc.experiments.composed_clearing import TWO_STEP_DECLARATION


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and replay the supplied two-step clearing timeline.")
    parser.add_argument("--json", action="store_true", help="Print the complete retained timeline as JSON.")
    return parser.parse_args(argv)


async def run_demo(json_output: bool) -> None:
    timeline = await run_timeline(TWO_STEP_DECLARATION)
    assert replay_timeline(TWO_STEP_DECLARATION, timeline) == timeline

    if json_output:
        print(json.dumps(timeline.as_json(), indent=2, sort_keys=True))
        return

    print(f"Declaration: {timeline.declaration.name}")
    for step in timeline.steps:
        print(f"Step {step.ordinal}: {step.resolution.outcome}")
        for actor_name, record in step.actors.items():
            print(f"  {actor_name} context: {record.retained_context}")
            print(f"  {actor_name} proposal: {record.proposal}")
        print(f"  resolution order: {', '.join(step.resolution.order)}")
        print(f"  transitions: {', '.join(step.resolution.transitions) or 'none'}")
    print("Replay: verified without actor mediation")


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(run_demo(args.json))


if __name__ == "__main__":
    main()
