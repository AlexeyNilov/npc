"""Launch the autonomous, observer-only clearing session."""

from __future__ import annotations

import argparse

from npc.experiments.autonomous_clearing import run_terminal


def main() -> None:
    parser = argparse.ArgumentParser(description="Observe a replayable autonomous clearing session.")
    parser.add_argument("--turn-limit", type=int, default=3, help="Authoritative launcher limit, from 1 through 10.")
    arguments = parser.parse_args()
    run_terminal(arguments.turn_limit)


if __name__ == "__main__":
    main()
