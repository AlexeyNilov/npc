# TASK-002: Add and test an authoritative trader-identity capability

**Status:** Planned

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** Accepted TASK-001 commit

**Depends on:** TASK-001

**Write scope:** `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`,
`docs/requirements.md`, `docs/architecture.md`

**Parallel-safe with:** None; it must compare its diff with the accepted
TASK-001 baseline.

**Durable information changed:**

- What must the system do? -> [Requirements](../requirements.md), Stateful
  conversational trader playtest.
- How does the system work now? -> [Architecture](../architecture.md),
  Conversational trader playtest.

**Simplifier review:** Required before handoff because the result adds a
capability to the shared authority boundary.

## Outcome

The terminal trader playtest supports one bounded, non-economic identity query
through the common authority flow alongside the existing purchase. A supported
identity query deterministically responds `The trader's name is Mara.` and
changes no state; unsupported identity-like messages produce no identity claim
and change no state. The task supplies the direct evidence required to accept
or reject Roadmap Outcome 6.

## Canonical context

- [Roadmap: Outcome 6](../roadmap.md#6-test-a-reusable-authoritative-action-boundary)
  defines the experiment, scope guard, and pass criterion.
- [Issue 001](../issues/ISSUE-001-social-dialogue-and-authority.md) defines the
  observed social-dialogue problem and open question.
- [Requirements: Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest)
  owns observable behavior.
- [Architecture: Conversational trader playtest](../architecture.md#conversational-trader-playtest)
  owns the verified common-flow description after this test passes.
- Initial entry points: `src/npc/trader_playtest.py`,
  `tests/test_trader_playtest.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and
only the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Add an identity capability contract whose sole authoritative fact is the
  immutable trader name `Mara`, whose sole supported action is
  `identify_trader`, and whose only outcome is the exact deterministic identity
  reply with no trader or player state mutation.
- Accept the action only when the untrusted candidate supplies that action and
  exact evidence matching the complete normalized player message
  `what is your name` (case and terminal punctuation may vary). The player
  message, not model prose or conversation history, is the authority for this
  request shape.
- Treat malformed candidates and all other messages, including requests that
  merely mention a name, as unsupported: do not render the name, change state,
  or emit a trade trace.
- Update Requirements with the identity capability's trigger, evidence rule,
  response, and no-state-change behavior. Update Architecture only with the
  verified common flow and the two concrete contracts; do not duplicate
  behavioral requirements there.
- Do not change the common authority-flow implementation or the trade
  capability contract from the accepted TASK-001 baseline. Do not add more
  social intents, free-form dialogue, a universal NPC DSL, multiple actors,
  persistence, dependencies, or an LLM-generated identity reply.

## Acceptance and verification

- First add failing behavioral tests for the fixed corpus below, using
  deterministic scripted model replies. For every corpus case, assert the
  rendered player text, trace presence/absence, history outcome, and equality
  of trader/player state before and after where no trade is authorized.

  | Capability | Message and candidate | Expected authoritative outcome |
  | --- | --- | --- |
  | Purchase | `I sell you a healing herb for 4 gold.` with valid trade candidate | Existing accepted purchase and unchanged `TRADE_TRACE` payload |
  | Purchase | `Will you sell me a healing herb for 4 gold?` with valid trade candidate | Unsupported; no state change or trace |
  | Identity | `What is your name?` with `identify_trader` and matching evidence | `The trader's name is Mara.`; no state change or trace |
  | Identity | `Tell me your name.` with `identify_trader` candidate | Unsupported; no name claim, state change, or trace |
  | Identity | `What is your name?` with malformed/wrong candidate | Unsupported; no name claim, state change, or trace |

- Run the corpus twice from equivalent fresh sessions and assert equal
  authoritative outcomes and states.
- Inspect the base-to-head diff against the accepted TASK-001 commit. It may add
  the identity contract and register it with the existing dispatch mechanism,
  but it must not alter the common-flow implementation or trade-contract
  definitions. If it does, stop and report the coupling; do not generalize
  further.
- Run `make test`, then `make check`, and `git diff --check`. Report exact
  results and the baseline diff inspection.

## Stop conditions

- TASK-001 is not accepted, does not expose a bounded common flow, or its
  trade behavior has regressed.
- Identity needs a change to common-flow code or the trade contract, a new
  authority decision, model-authored reply text, an additional capability, or
  a dependency.
- The test demonstrates coupling instead of the pass criterion. Preserve the
  evidence, update no architecture claim, and return the task for planner
  decision.
- A needed durable fact has no canonical owner, or unexpected user-owned edits
  overlap the write scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
