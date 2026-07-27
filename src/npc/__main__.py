from __future__ import annotations

import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .simulation import load_scenario, resolve, select_proposal


def main() -> None:
    path = Path(sys.argv[1])
    state, rules = load_scenario(path)
    turn_limit = yaml.safe_load(path.read_text())["turn_limit"]
    for _ in range(turn_limit):
        proposal = select_proposal(state, rules)
        if proposal is None:
            break
        print(resolve(state, proposal).narration)


if __name__ == "__main__":
    main()
