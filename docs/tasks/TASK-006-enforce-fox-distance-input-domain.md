# TASK-006: Reject invalid fox starting distances before turn processing

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `2ab6804`

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_distance_feedback.py`,
`sample/fox_chat.py`, `tests/test_fox_distance_feedback.py`,
`tests/test_fox_chat.py`, `docs/requirements.md`, `docs/architecture.md`, and
`docs/issues/ISSUE-002-distance-input-domain.md`

**Parallel-safe with:** None — the same authoritative input boundary is used by
the module, fixtures, and chat sample.

**Durable information changed:** What must the system do? ->
[Requirements](../requirements.md), Bounded fox distance feedback. How does the
system work now? -> [Architecture](../architecture.md), Bounded fox distance
feedback. What observed problems remain unresolved? ->
[ISSUE-002](../issues/ISSUE-002-distance-input-domain.md).

**Simplifier review:** Required — this changes a callable authoritative input
contract used across direct, fixture, and chat paths.

## Outcome

`run_turn` enforces the already accepted authoritative starting-distance domain:
only non-boolean integers greater than or equal to `1` are valid. Any other
value raises `ValueError` before hearing, sensor invocation, action execution,
or feedback can occur.

## Canonical context

- [Bounded fox distance feedback requirement](../requirements.md#bounded-fox-distance-feedback).
- [Bounded fox distance feedback architecture](../architecture.md#bounded-fox-distance-feedback).
- [ISSUE-002](../issues/ISSUE-002-distance-input-domain.md).
- Initial source and test entry points:
  `src/npc/experiments/fox_distance_feedback.py`,
  `sample/fox_chat.py`, `tests/test_fox_distance_feedback.py`, and
  `tests/test_fox_chat.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and
only the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Define and enforce the accepted domain at `run_turn`, the authoritative
  boundary. Do not duplicate domain policy in the CLI, fixture loader, or chat
  loop.
- Treat `bool` as invalid even though Python makes it a subclass of `int`.
- Preserve current behavior for every valid integer distance and the existing
  checked-in fixtures.
- Update the verified mechanism documentation, then resolve the issue with the
  verification evidence. Keep the accepted behavior in Requirements unchanged
  unless implementation evidence exposes a conflict.
- Exclusions: coercion or clamping, a generic numeric/domain abstraction,
  changes to hearing or displacement values, and broader actor/world state work.

## Acceptance and verification

- Add failing behavioral tests before implementation: negative integers,
  `True`, and a non-integer each raise `ValueError` from `run_turn` and make no
  completion call.
- Add a chat-path test showing an invalid starting distance surfaces the same
  failure without invoking completion or narration.
- Existing valid values, including `1`, `10`, and out-of-range values above
  `10`, retain their current traces and feedback behavior.
- Fixture and CLI paths rely on the `run_turn` validation rather than a second
  implementation of the domain rule.
- Run the focused fox distance and chat tests, then `make check` and
  `git diff --check`.

## Stop conditions

- Any request to normalize invalid values, accept non-integer distances, or
  alter the units/minimum distance requires a new product contract decision.
- Unexpected behavior change to valid checked-in fixtures, required changes
  outside the stated write scope, or user-owned overlapping edits.
- A reason the failure cannot be represented as `ValueError` at `run_turn`.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
