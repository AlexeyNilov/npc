from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .simulation import (
    PerceptionError,
    format_turn_record,
    load_scenario,
    narrate,
    perceive,
    resolve,
    select_proposal,
    turn_record,
)


def main() -> int:
    path = Path(sys.argv[1])
    state, rules, perception = load_scenario(path)
    turn_limit = yaml.safe_load(path.read_text())["turn_limit"]
    for _ in range(turn_limit):
        try:
            answers = asyncio.run(perceive(state, perception))
        except PerceptionError as error:
            print(f"perception error: {error}", file=sys.stderr)
            return 1
        proposal = select_proposal(state, rules, answers)
        if proposal is None:
            break
        outcome = resolve(state, proposal)
        print(format_turn_record(turn_record(perception.questions, answers, proposal, outcome)))
        narration = asyncio.run(narrate(proposal, outcome))
        print(f"non-authoritative narration: {narration or 'unavailable'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
