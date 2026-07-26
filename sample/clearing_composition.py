#!/usr/bin/env python3
"""Run a supplied clearing composition declaration.

See docs/builder-guide.md for the builder workflow and authority boundaries.

Run from the repository root:
    PYTHONPATH=src .venv/bin/python sample/clearing_composition.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence

from npc.composition import CompositionDeclaration, replay, run
from npc.experiments.composed_clearing import (
    BASELINE_DECLARATION,
    CAUTIOUS_FOX_DECLARATION,
    FOX_FIRST_RULES_DECLARATION,
)

DECLARATIONS: dict[str, CompositionDeclaration] = {
    "baseline": BASELINE_DECLARATION,
    "cautious-fox": CAUTIOUS_FOX_DECLARATION,
    "fox-first": FOX_FIRST_RULES_DECLARATION,
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and replay a supplied clearing composition.")
    parser.add_argument("--scenario", choices=sorted(DECLARATIONS), default="baseline", help="Composition declaration to run.")
    parser.add_argument("--json", action="store_true", help="Print the complete retained trace as JSON.")
    return parser.parse_args(argv)


async def run_scenario(scenario: str, json_output: bool) -> None:
    declaration = DECLARATIONS[scenario]
    trace = await run(declaration)
    assert replay(declaration, trace) == trace

    if json_output:
        print(json.dumps(trace.as_json(), indent=2, sort_keys=True))
        return

    print(f"Declaration: {trace.declaration.name}")
    print(f"Rules: {trace.declaration.simulation_name}")
    for actor_name, record in trace.actors.items():
        print(f"{actor_name}: {record.component_name}")
        print(f"  shown: {record.shown_input}")
        print(f"  cognition: {record.cognition}")
        print(f"  proposal: {record.proposal}")
    print(f"Resolution order: {', '.join(trace.resolution.order)}")
    print(f"Outcome: {trace.resolution.outcome}")
    for actor_name, feedback in trace.resolution.feedback.items():
        print(f"{actor_name} feedback: {feedback}")
    print("Replay: verified without actor mediation")


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(run_scenario(args.scenario, args.json))


if __name__ == "__main__":
    main()
