# ISSUE-002: Fox distance accepts values outside a physical distance domain

**Status:** Open

**Observed:** 2026-07-25

**Scope:** Bounded fox distance-feedback experiment input contract

## Problem

`run_turn` accepts its `starting_distance` as an integer without enforcing a
non-negative distance domain. A negative distance is treated as audible and is
retained as feedback. Python booleans also satisfy the `int` annotation at
runtime.

## Evidence

- Running:

  ```sh
  .venv/bin/python -c 'import asyncio; from npc.experiments.fox_distance_feedback import run_turn; completion = lambda _prompt, _system: __import__("asyncio").sleep(0, result="{\"threat\": false, \"certainty\": 0.5, \"evidence\": null}"); trace = asyncio.run(run_turn("Fox, hello.", -1, completion)); print(trace.heard, trace.starting_distance, trace.resulting_distance)'
  ```

  prints `True -1 -1`.
- The checked-in fixtures use valid non-negative integer distances, so the
  completed experiment's observed behavior remains reproducible.

## Impact

The current trusted-fixture experiment remains bounded and valid, but distance
cannot be promoted as a durable world-state boundary until its accepted input
domain and invalid-input behavior are explicit.

## Open question

What values constitute valid authoritative distance, and how should the system
handle invalid values before they can affect hearing, action execution, or
feedback?

## Routing

- **Requirements:** [Bounded fox distance feedback](../requirements.md#bounded-fox-distance-feedback).
- **Architecture:** [Bounded fox distance feedback](../architecture.md#bounded-fox-distance-feedback).
- **Decision:** None.
- **Roadmap:** None.
- **Task:** None.

## Resolution

Pending.
