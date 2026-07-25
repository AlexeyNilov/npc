# TASK-001: Run a stateful conversational trader playtest

**Status:** Ready

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `292776f`

**Depends on:** None

**Write scope:** `src/npc/`, `tests/`, `README.md`, `docs/architecture.md`

**Parallel-safe with:** None — this task changes the trader's public terminal
entry point and the shared deterministic decision module.

**Durable information changed:**

- What must the system do? -> [Requirements](../requirements.md),
  `Stateful conversational trader playtest` (already planned).
- How does the system work now? -> [Architecture](../architecture.md), add the
  verified playtest flow after implementation.
- What is this project, and how do I use it? -> [README](../../README.md), add
  the verified run instructions after implementation.

**Simplifier review:** Required — the work introduces a new public terminal
boundary, LLM-to-engine integration, and cross-module state flow.

## Outcome

A developer with the configured local LLM can run a terminal-only, single
process trader conversation, make natural-language trade proposals, and observe
LLM narration that reflects the current authoritative state and relevant
in-session history. The terminal exposes enough structured evidence to replay
each deterministic trade decision.

## Canonical context

- [Roadmap](../roadmap.md), `3. Run a stateful conversational trader playtest`.
- [Requirements](../requirements.md), `Trader decision experiment` and
  `Stateful conversational trader playtest`.
- [Decisions](../decisions.md), `Keep core actor decisions deterministic` and
  `Use a local-LLM terminal session for the first trader playtest`.
- Initial implementation: `src/npc/trader_experiment.py`,
  `src/npc/infrastructure/language_model.py`, `sample/chat.py`.
- Initial tests: `tests/test_trader_experiment.py`, `tests/test_config.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the
[Implementer guide](../agent_roles/implementer.md), and only the context named
above. Do not read the task registry, sibling packets, completed tasks, or
unrelated planning history.

## Task-specific scope

- Add `python -m npc.trader_playtest` as the interactive terminal entry point;
  `/exit` and EOF must end it cleanly.
- Reuse the configured local LLM transport, but introduce a testable boundary
  that receives the current state and relevant session history, returns
  narration plus one constrained candidate trade, and cannot mutate state.
- Support only the existing one-herb player-to-trader sale and integer gold
  price. Validate candidate output before creating an `Offer`; unsupported or
  malformed output is conversational only and must not change state.
- Maintain trader/player state and history in memory only. Each valid offer
  must call `evaluate_offer` (or a behavior-preserving deterministic successor)
  and use its returned states for every later turn.
- Print a concise, machine-readable-or-copyable per-trade trace containing the
  candidate proposal, decision reason, and pre/post states. Preserve the
  current scenario command and its independent-case semantics.
- Write behavioral tests before behavior-changing logic. Mock the LLM boundary;
  do not require a network service in automated tests.
- After verified implementation, document the run command/configuration in the
  README and the actual component/data flow in Architecture. Do not alter the
  roadmap, requirements, or accepted decisions without new planning evidence.

**Explicit exclusions:** browser UI; persistence across program restarts;
multi-actor or multi-item commerce; new economic rules; LLM-authoritative state
changes; production telemetry or remote-service setup.

## Acceptance and verification

- A mocked two-or-more-turn test proves that an accepted trade changes the
  state supplied to the next LLM turn and that a repeated/follow-up proposal
  receives the deterministic outcome implied by that changed state.
- Tests prove the model cannot override the engine: accepted and refused
  candidates use the engine's reason and resulting states; malformed and
  unsupported candidates leave state unchanged.
- A terminal test proves a trade trace includes candidate, reason, and both
  parties' before/after state. A separate regression test preserves
  `python -m npc.trader_experiment` output/semantics.
- Run `pytest`, `ruff check .`, `mypy`, `git diff --check`, and the repository's
  applicable aggregate check if one is present.
- Manually run the documented command against the configured local LLM. Record
  a short playtest transcript outside durable docs that includes a follow-up or
  repeated proposal and shows its state- or history-dependent difference.

## Stop conditions

- The local endpoint cannot return a reliably constrained candidate format and
  no deterministic validation/fallback preserves the authority boundary.
- A required behavior conflicts with the roadmap constraint or either accepted
  decision.
- The task needs persistence, a browser surface, additional trade types, or
  LLM-authoritative decision making.
- Unexpected user-owned changes overlap this task's write scope, or required
  local-LLM access is unavailable for the manual playtest.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
