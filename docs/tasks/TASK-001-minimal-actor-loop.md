# TASK-001: Demonstrate a minimal deterministic actor loop

**Status:** Done

**Owner:** task_001_actor_loop

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `ba57a73`

**Depends on:** None

**Write scope:** `src/npc/`, `tests/`, `docs/requirements.md`,
`docs/architecture.md`

**Parallel-safe with:** None — this changes the current shared authority flow
and its canonical documentation.

**Durable information changed:**

- What the system must do -> [Requirements](../requirements.md), new
  actor-loop experiment heading.
- How the system works now -> [Architecture](../architecture.md), new
  deterministic actor-loop heading.

**Simplifier review:** Required — this task introduces a candidate reusable
system boundary and a cross-module change.

## Outcome

Two distinct, bounded action contracts run through one deterministic,
terminal-independent actor loop and produce an inspectable record from
reality through feedback. This tests whether the project vision's actor loop
is a reusable boundary while preserving authoritative deterministic state and
choice.

## Vision alignment

- **Vision behavior made observable:** An actor's reality, perception,
  sensemaking, intent, action, outcome, and feedback visibly explain its
  authoritative choices.
- **Classification:** `Candidate durable system foundation`
- **Reuse pressure:** A state-changing healing-herb purchase and a
  state-preserving supported trader-identity response use different action
  contracts through the same loop.
- **Boundary rejection signal:** Stop promotion if either scenario requires a
  trader-, herb-, gold-, identity-, or terminal-chat-specific branch in shared
  orchestration; different stage sequencing; or a record that cannot reproduce
  its authoritative outcome.

## Canonical context

- [Roadmap Outcome 1](../roadmap.md#1-test-a-minimal-reusable-actor-loop-model)
  defines the pass criterion.
- [Keep core actor decisions deterministic](../decisions.md#2026-07-25-keep-core-actor-decisions-deterministic)
  and [Test a narrow deterministic actor-loop boundary](../decisions.md#2026-07-25-test-a-narrow-deterministic-actor-loop-boundary)
  define the authority constraint and accepted boundary choice.
- [Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest)
  defines current observable behavior.
- [Conversational trader playtest](../architecture.md#conversational-trader-playtest)
  describes the current `AuthorityFlow` and capability dispatch.
- Initial source and test entry points: `src/npc/trader_playtest.py`,
  `src/npc/trader_experiment.py`, and `tests/test_trader_playtest.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and
only the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Introduce the narrow loop boundary and explicit, inspectable stage record.
  It owns deterministic sequencing and state threading only.
- Adapt the existing healing-herb purchase and supported identity contracts to
  run through that loop without changing their accepted player-visible
  behavior.
- Ensure perception is derived only from authoritative reality, the player
  message, and deterministically validated untrusted model output. The LLM
  cannot authoritatively select an intent, action, state change, or final
  choice.
- Add focused tests using deterministic model replies or normalized candidates;
  do not use a live local LLM to establish repeatability.
- After verified behavior, add only the corresponding requirement and current
  architecture facts to their canonical owners.

**Assumptions:** The current purchase and exact identity contracts are the two
scenarios; identity continues to preserve state and emits no trade trace.

**Exclusions:** New dialogue, action contracts, persistence, generic actor
goals or memory, generalized world state, browser UI, LLM changes, and changes
to the accepted authority decisions.

## Acceptance and verification

- A behavioral test is added and fails before the application logic changes.
- The same loop entry point runs both fixed scenarios and returns a record with
  all seven named stages.
- Purchase fixture: from the documented initial state, the evidence-validated
  offer `I sell you a healing herb for 4 gold.` produces deterministic accepted
  state changes, conserves gold and herbs, and records the decision reason.
- Identity fixture: `What is your name?` with the supported candidate returns
  Mara's identity, preserves both states, and records no trade trace.
- Re-running each fixture from identical reality and identical validated input
  yields identical authoritative intent, outcome, state, and feedback. Model
  flavor is excluded from this authority comparison.
- The shared loop contains no scenario-specific branches or values for trader,
  herb, gold, identity, or terminal chat.
- Existing trader-playtest requirements remain covered by regression tests.
- Run the focused new/changed behavioral tests, then `make check` and
  `git diff --check`.

## Stop conditions

- The required second scenario needs a different orchestration sequence or a
  shared-loop scenario-specific branch.
- Any implementation makes a model response authoritative for intent, action,
  state transition, or final choice.
- The change requires a new action contract, persistence, generalized
  memory/goals/world state, or a new dependency.
- Existing user-owned changes overlap the write scope, or evidence conflicts
  with a canonical owner.
- Missing access, fixture, or specification prevents deterministic verification.

## Handoff

**Status and outcome:** Done — both the state-changing purchase and
state-preserving identity contracts run through one terminal-independent,
seven-stage deterministic loop with reproducible authoritative records.

**Changed files and ownership impact:** `src/npc/actor_loop.py` establishes
the narrow loop; `src/npc/trader_playtest.py` adapts both contracts; tests
cover the experiment and playtest regression. [Requirements](../requirements.md)
now owns the new observable behavior and [Architecture](../architecture.md)
owns the verified current design.

**Verification:** Initial focused behavioral test failed before loop logic with
missing `TraderSession.last_actor_record`. After implementation and simplifier
correction: `.venv/bin/pytest tests/test_actor_loop.py tests/test_trader_playtest.py`
passed (17 tests); `make check` passed (26 tests); final `git diff --check`
passed.

**Assumptions, risks, and next action:** Identical validated input means the
same normalized candidate; closed model flavor remains non-authoritative. The
boundary is a candidate durable foundation, not proof of a universal actor
model. Next action is Roadmap Outcome 2 only after deciding to run the bounded
trader playtest.
