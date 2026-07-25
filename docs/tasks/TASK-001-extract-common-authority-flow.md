# TASK-001: Extract the common authority flow without changing trade behavior

**Status:** Ready

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `0f18b4c`

**Depends on:** None

**Write scope:** `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`

**Parallel-safe with:** None; TASK-002 depends on this task's accepted result.

**Durable information changed:** None. This task preserves the existing observable
trade contract; the verified shared design is owned by Architecture only after
TASK-002 proves it with a second capability.

**Simplifier review:** Required before handoff because this task introduces a
shared authority boundary.

## Outcome

The existing healing-herb purchase runs through a capability-independent
authority flow while preserving its current player-visible replies, evidence
validation, authoritative state transitions, history, and `TRADE_TRACE` shape.
This establishes a baseline from which a second capability can be added without
altering the flow or the trade contract.

## Canonical context

- [Roadmap: Outcome 6](../roadmap.md#6-test-a-reusable-authoritative-action-boundary)
  defines the hypothesis and pass criterion.
- [Requirements: Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest)
  is the existing observable trade contract to preserve.
- [Decision: Gate trade extraction with verbatim player-message evidence](../decisions.md#2026-07-25-gate-trade-extraction-with-verbatim-player-message-evidence)
  and [compose trade replies from authoritative results](../decisions.md#2026-07-25-compose-trade-replies-from-authoritative-results)
  preserve the deterministic boundary.
- Initial entry points: `src/npc/trader_playtest.py`,
  `tests/test_trader_playtest.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and
only the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Extract a single common flow that accepts an untrusted interpretation,
  dispatches it to a bounded capability contract, validates message evidence,
  obtains an authoritative outcome, renders player text from that outcome, and
  records the turn and any trace.
- Keep the healing-herb purchase as one capability contract. Its contract owns
  its schema, exact evidence grammar, call to `evaluate_offer`, state mutation,
  possible results, rendered trade text, and trade trace payload.
- Preserve the public terminal command and model-transport behavior. Do not add
  a second capability, a generic DSL, persistence, dependencies, or model prose.
- The extracted API may be internal and should contain only concepts exercised
  by this contract and TASK-002; do not pre-generalize for future capabilities.

## Acceptance and verification

- First add or adapt a behavioral regression test proving that an accepted trade
  still emits the existing reply and trace payload, and that each unsupported,
  malformed, and refused trade leaves the appropriate state unchanged.
- The complete current trader-playtest corpus passes unchanged after the
  extraction, including exact reply assertions and deterministic repeatability.
- A focused test demonstrates that the common flow, rather than terminal-loop
  branching, invokes the trade capability's validation, authoritative outcome,
  rendering, and trace handling.
- Run `make test`, then `make check`, and `git diff --check`. Report exact
  results and the base-to-head diff paths. If `make check` reformats files,
  inspect and retain only formatting that belongs to the task.

## Stop conditions

- The current requirements or accepted decisions cannot be preserved without
  changing an observable trade reply, validation rule, trace field, or model
  boundary.
- The proposed boundary needs a universal schema/DSL, a new dependency, or a
  decision about authority not supplied by the canonical context.
- A needed durable fact has no canonical owner, or unexpected user-owned edits
  overlap the write scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
