# TASK-001: Run, inspect, and replay one autonomous clearing session

**Status:** In progress

**Owner:** autonomous_clearing

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `b11b3469320c9ef4c7fa0e1d2fe8221bdc571019`

**Depends on:** None

**Write scope:**
`src/npc/experiments/autonomous_clearing.py`,
`sample/autonomous_clearing.py`, `tests/test_autonomous_clearing.py`,
`README.md`, `docs/architecture.md`, this packet, and `docs/tasks/STATUS.md`.

**Parallel-safe with:** None — this cross-module delivery owns its listed files.

**Durable information changed:**
`What is this project, and how do I use it?` -> `README.md` (the observer
entry point); `How does the system work now?` -> `docs/architecture.md`
(only after verification). Requirements and decision rationale are accepted
context and are out of scope.

**Simplifier review:** Required — new scenario-local runtime, terminal entry
point, and cross-module changes.

## Outcome

An observer can launch the supplied terminal clearing session and watch it run
to an ending without providing any input. Each turn exposes its retained LLM
prompts and raw responses alongside a readable causal account; after the
ending, the observer can inspect, exactly replay, or start another run without
providing a causal choice. The session records a launcher-supplied turn limit
and selected events, and reaches `fed`, `caught`, or `clearing_quiet` under the
accepted scenario rules.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Turn limit `N` | [Autonomous observer clearing session requirement](../requirements.md#autonomous-observer-clearing-session) | Non-boolean integer 1–10, supplied at start and retained by value | Launcher input becomes authoritative initial configuration; observer controls cannot change it | Validated before selection; retained in each session record; replay verifies it | Accepted in [autonomous-observer decision](../decisions.md#2026-07-26-run-the-clearing-as-an-autonomous-observer-simulation) |
| `food_scent` / `trap_materials_arrive` | [Autonomous observer clearing session requirement](../requirements.md#autonomous-observer-clearing-session) | Uniform selection with replacement; each applies only its specified canonical effect and visibility | Simulation | Selected and recorded before effect; replay consumes recorded selection | Accepted requirement |
| `fed`, `caught`, `clearing_quiet` | [Autonomous observer clearing session requirement](../requirements.md#autonomous-observer-clearing-session) | The only session endings, selected by resolution or after `N` resolved turns | Simulation | Terminal; prohibits later event selection | Accepted requirement |
| Actor-local cognition and observer narration | [Autonomous observer clearing session requirement](../requirements.md#autonomous-observer-clearing-session) | One real-LLM cognition call per actor turn and one post-completion narration call; outputs are recorded presentation only | No authority; deterministic policy and simulation retain authority | Fresh run calls the configured LLM; replay consumes its retained records | Accepted in [autonomous-observer decision](../decisions.md#2026-07-26-run-the-clearing-as-an-autonomous-observer-simulation) |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Observer, controlled variation, simulation event, replayable / reproducible | Existing [Glossary](../glossary.md) entries | Shared product, authority, and record boundary terms |
| Session record, turn record, structured fallback | Packet-local implementation names | Keep the delivery scenario-local; do not add glossary terms unless accepted reuse needs arise |

## Experiment evidence

Not applicable — direct delivery.

## Vision alignment

Not applicable — this delivery is explicitly scenario-local and does not claim
a reusable system boundary.

## Canonical context

- [Autonomous observer clearing session](../requirements.md#autonomous-observer-clearing-session).
- [2026-07-26: Run the clearing as an autonomous observer simulation](../decisions.md#2026-07-26-run-the-clearing-as-an-autonomous-observer-simulation).
- [Deliver one complete autonomous clearing session](../roadmap.md#1-deliver-one-complete-autonomous-clearing-session).
- [Builder-controlled clearing composition](../architecture.md#builder-controlled-clearing-composition), as a boundary to preserve rather than extend.
- Initial source/test entry points: `src/npc/composition.py`,
  `src/npc/experiments/composed_clearing.py`, and
  `tests/test_composition.py`.

## Task-specific scope

- Implement one self-contained clearing-session runtime with its own state,
  deterministic event selection seam, actor policies, causal records, replay,
  and presentation formatter. Do not modify `npc.composition` or the existing
  composed-clearing experiment.
- Use the accepted event vocabulary and resolution ordering exactly. Select
  events using an injected scenario-local random source in new runs; retain
  selected values for replay instead of relying on a seed or selecting again.
- Make `N` a launcher argument to the runtime, validate it before any event or
  actor work, retain it in the session record, and do not expose it as an
  interactive observer control.
- Provide a standard-library terminal path that starts and completes the
  session automatically, printing every retained LLM prompt and raw response
  or unavailable marker with each readable causal account. After completion,
  offer inspection, exact replay, and fresh-run controls. A launcher may
  configure `N`; the observer cannot.
- Make one configured real-LLM cognition call per actor turn with only that
  actor's filtered observation and own feedback context, then retain its prompt,
  raw output or null, validation status, and accepted JSON `question` and
  `sensemaking` values or actor-local fallback. The cognition cannot alter
  deterministic proposal selection.
- Make one configured real-LLM narration call after each completed turn, using
  only retained causal facts. Validate it as non-authoritative and fall back to
  a fixed, readable account derived only from the retained turn record.
- Do not add dependencies, persistence, a generic event/randomness/scheduler
  API, branching, another scenario, model-mediated proposal behavior, or
  changes to accepted requirements and decisions.

## Acceptance and verification

- Start with failing behavioral tests for the scenario runtime, then implement
  only enough behavior to satisfy them.
- Test `N` accepts only non-boolean integers 1–10 and rejects invalid values
  before the event source or actor policies are invoked.
- With deterministic injected selections, prove: first-turn `food_scent`
  ends `fed`; `trap_materials_arrive` followed later by `food_scent` ends
  `caught`; and no `food_scent` through `N` ends `clearing_quiet`. Verify
  replacement selection by covering repeated `trap_materials_arrive`.
- For every recorded turn, assert causal ordering, by-value JSON safety,
  filtered observations, actor-local retained feedback, one actor-local LLM
  cognition call per actor, deterministic policy proposals, hunter-before-fox
  resolution, and simulation-only state changes.
  Include source-variation tests that change recorded event histories and show
  corresponding proposal/outcome changes, plus withheld-fact tests for each
  actor boundary.
- Replay a session without invoking the selector, actor LLM, or narrator, and
  assert it preserves the retained cognition and narration. It may
  deterministically re-derive the accepted proposal from the recorded filtered
  observation; this is validation, not actor mediation. Mutate each required
  authoritative fact class — including missing/reordered event, event
  ordinal/name/effect, `N`, observation/context, proposal, resolution/feedback,
  state, and ending — and assert rejection.
- Exercise the terminal path through injected input/output: launch advances to
  an ending without observer input; each turn exposes both actor and narration
  prompts/raw outputs; inspection is read-only; replay is exact; and fresh run
  creates a new record without an observer causal choice.
- Exercise blank, malformed, unavailable, and exceptional actor-cognition and
  narration paths and assert their fixed fallbacks leave authoritative facts
  unchanged.
- Run `.venv/bin/pytest tests/test_autonomous_clearing.py`, `make check`, and
  `git diff --check`. At Review, perform Simplifier review, inspect the final
  diff, update only the README and Architecture facts established by the
  delivery, and complete the requirement-to-evidence closure audit.

## Stop conditions

- A requirement or decision conflicts with the accepted event, visibility,
  actor-policy, ending, or `N` rules.
- The implementation requires a generic composition, event, scheduling,
  randomness, persistence, or presentation framework.
- A new domain label, state field, event, transition, or threshold is needed
  beyond the accepted contract.
- The terminal control behavior cannot remain noncausal, or required replay
  evidence needs fresh selection, actor mediation, or model invocation.
- Unexpected user-owned edits overlap the write scope, or required tooling is
  unavailable.

## Handoff

**Status and outcome:** In progress; the accepted terminal interaction changed
from observer-driven turn stepping to automatic session progression with
visible retained LLM exchanges.

**Changed files and ownership impact:** Added the scenario runtime, terminal
launcher, and behavioral tests; README owns the observer entry point and
Architecture owns the verified scenario boundary. Requirements and Decisions
remain user-owned context.

**Verification:** Review revisions: `.venv/bin/pytest
tests/test_autonomous_clearing.py` (10 passed); `make check` (59 passed); `git
diff --check` passed. Focused tests cover causal ordering, final-turn narration
facts, replay isolation, required authority mutations, all required fallback
categories, exact replay of a three-turn `clearing_quiet` session, readable
retained-record inspection, a nonterminal pause, and clean fresh-run history.

**Assumptions, risks, and next action:** The configured LLM adapter uses the
existing local `complete_text` client; unavailable or invalid output visibly
falls back without changing authority. Revise the terminal surface and its
behavioral tests for automatic progression and visible retained exchanges, then
return to Simplifier review.
