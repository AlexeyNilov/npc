# TASK-001: Establish one language-mediated causally closed actor turn

**Status:** Ready

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `db09f7a580342e3f81e9ffc5446847de2e8c4429`

**Depends on:** None

**Write scope:**
`src/npc/experiments/fox_causal_turn.py`,
`tests/test_fox_causal_turn.py`,
`scenarios/fox_causal_turn.yaml`,
and `docs/architecture.md`.

**Parallel-safe with:** `None` — the delivery changes a new actor-loop path and
the canonical records that describe it.

**Durable information changed:**

- How does the system work now? -> [Architecture](../architecture.md), new
  verified causal-turn design heading.

**Simplifier review:** Required before acceptance: this introduces a new
cross-module actor-to-simulation-core boundary.

## Outcome

In one checked-in bounded scenario, a fox receives only a simulation-filtered
natural-language observation, forms a recorded subjective percept through its
epistemic profile, receives separately retained answers and percept evidence
for two or more ordered actor-owned questions from one mediation request,
submits a bounded proposal, and receives authoritative feedback after the
simulation core resolves and commits the transition. A recorded trace replays
the committed transition without regenerating actor cognition. This establishes
Horizon 1 causal closure while keeping the slice fox-local rather than claiming
a reusable actor or world framework.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Actor-accessible substate | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn), [Glossary](../glossary.md#actor-loop-terms) | Simulation deterministically derives the accepted clearing/smell/rustling observation from canonical state and withholds the blocked path before mediation. | Simulation core | Per turn, retained in trace | No new decision. |
| Epistemic profile | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn), [Decisions](../decisions.md#2026-07-26-use-natural-language-as-the-default-actor-world-semantic-interface) | The accepted hungry/cautious fox context shapes only its subjective percept. | Actor | Per turn, retained in trace | No new decision. |
| Subjective percept | [Glossary](../glossary.md#actor-loop-terms), same decision | One recorded natural-language percept generated from the accessible substate and profile; it never changes canonical reality. | Actor-local mediation output | Per turn, retained in trace | No new meaning. |
| Actor-owned question and percept evidence | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn), [Glossary](../glossary.md#actor-loop-terms) | The accepted ordered threat and food-reachability questions are evaluated together against one percept; each answer retains its supporting percept reference. | Actor | Per turn, retained in trace | No new decision. |
| Action proposal, resolution, feedback | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn), [Strategy](../strategy.md#strategic-constraints) | The fox may propose `approach_food` or `wait`; the core alone resolves the blocked path, commits `food_path_blocked` or waiting, and returns accepted feedback. | Proposal: actor; resolution and state: simulation core | Per turn, retained in trace; committed state carries forward | No new decision. |
| Controlled variation | [Glossary](../glossary.md#authority-and-state), [Decisions](../decisions.md#2026-07-26-define-determinism-as-replayable-authoritative-causality) | Omit from this first slice unless an accepted scenario requires it; if used, record it in the trace. | Declared boundary only | Per turn, retained in trace | No variation is currently authorized. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| actor-accessible substate, epistemic profile, subjective percept, actor-owned question, percept evidence, action proposal, feedback, causal closure | Existing [Glossary](../glossary.md) entries | Preferred shared names for the actor/simulation boundary and trace. |
| fox_causal_turn | Packet-local implementation name | Names this one fox-local delivery slice; it does not name a reusable engine boundary. |
| `approach_food`, `wait`, `food_path_blocked` | Scenario-local labels defined by [Requirements](../requirements.md#fox-language-mediated-causal-turn) | Their meaning is limited to this accepted fox scenario; they do not warrant reusable glossary entries. |

## Experiment evidence

Not applicable. This is delivery against an agreed strategic boundary; it is
not an experiment.

## Vision alignment

- **Vision behavior made observable:** An actor interprets a limited view and
  proposes an action while the simulation remains the authoritative referee;
  the resulting causal path can be inspected and replayed.
- **Classification:** `Disposable experiment scaffolding`
- **Reuse pressure:** Not in scope — scaffolding only. Outcome 2 evaluates the
  independent actor-description seam after this slice exists.
- **Boundary rejection signal:** Any implementation requirement for actor
  cognition to traverse the canonical scenario schema, or for generated output
  to determine a transition, stops this task for Technical Lead review.

## Canonical context

- [Roadmap: Establish one language-mediated causally closed actor turn](../roadmap.md#1-establish-one-language-mediated-causally-closed-actor-turn).
- [Strategy: Current focus](../strategy.md#current-focus) and [Strategic
  constraints](../strategy.md#strategic-constraints).
- [Decision: Use natural language as the default actor-world semantic
  interface](../decisions.md#2026-07-26-use-natural-language-as-the-default-actor-world-semantic-interface).
- [Decision: Define determinism as replayable authoritative
  causality](../decisions.md#2026-07-26-define-determinism-as-replayable-authoritative-causality).
- Current related implementation and tests:
  `src/npc/experiments/fox_deterministic_utility.py` and
  `tests/test_fox_deterministic_utility.py`. They are foundational inputs only;
  do not extend their fox-local sensor/utility policy as the new boundary.
- [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn).

## Task-specific scope

- Add one dedicated fox-local causal-turn module, fixture scenario, and
  behavioral tests. Keep the existing distance-feedback, utility, rendering,
  and interactive-chat contracts unchanged.
- Define a narrow injected mediation boundary that receives only the
  actor-accessible substate, epistemic profile, and ordered questions. It makes
  exactly one request for the percept and answers, then validates the recorded
  shape before actor intent can use it.
- Retain the complete input and resolution chain needed to replay the
  authoritative transition: initial canonical state, derived accessible
  substate, profile, percept, ordered questions, individual answers with
  percept evidence, proposal, resolution, resulting canonical state, feedback,
  and any accepted controlled variation.
- Record only the verified mechanism in Architecture. Do not add a registry,
  DSL, class hierarchy, generic actor/world framework, scheduler, conflict
  machinery, renderer, or new dependency.
- Do not reuse current sensor candidates as percept evidence: they cite player
  text, whereas this outcome requires evidence that refers to the recorded
  subjective percept.

## Acceptance and verification

- The checked-in scenario demonstrates that the exact clearing/smell/rustling
  substate and accepted profile reach the sole LLM mediation request while the
  blocked path does not; it retains both ordered questions, one subjective
  percept, individually retained answers/evidence, the `approach_food`
  proposal, the `food_path_blocked` resolution, committed clearing state, and
  blocked-path feedback.
- Behavioral tests prove that withheld canonical facts do not enter the
  mediation input or actor-local records; generated percepts and answers do not
  alter canonical reality directly; and only the simulation-core resolver can
  commit a transition.
- Behavioral tests prove malformed mediation output, an answer without valid
  percept evidence, a rejected percept, and an unsupported or invalid proposal
  fail closed and produce no unauthorized canonical transition.
- Replay uses the recorded trace rather than a new LLM request and reproduces
  the committed transition. Tests distinguish an actor's false or incomplete
  belief from canonical state.
- Write failing behavioral tests before each behavior-changing implementation
  increment. Run the focused causal-turn tests, then `make check` and `git diff
  --check`.

## Stop conditions

- Stop for any requested reusable abstraction, changed strategy constraint,
  non-fox scenario, external LLM mutation, dependency, or a new semantic field
  whose source, transformation, authority, or lifecycle is absent from accepted
  context.
- Stop if replay cannot reproduce the committed transition using the recorded
  trace, or if the proposed scenario needs scheduling or conflict resolution
  beyond one actor turn.

## Handoff

**Status and outcome:** Ready; the Product Manager accepted the bounded fox
scenario in [Requirements](../requirements.md#fox-language-mediated-causal-turn).

**Changed files and ownership impact:** This packet and the open-task registry
only. They record task readiness; the Product Manager's requirements change
remains the canonical behavior owner.

**Verification:** Packet context and existing fox implementation/test path were
inspected. Final delivery verification is specified above.

**Assumptions, risks, and next action:** The accepted scenario deliberately
demonstrates an actor-local false belief; its percept evidence must not be
treated as canonical proof. Assign this Ready packet to one Implementer, who
must work test-first and stop on any semantic expansion.
