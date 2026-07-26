# TASK-001: Make the first actor-description boundary inspectable

**Status:** Ready

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** baf04f446e3562fd671060fd8665ee13b425c2f4

**Depends on:** None

**Write scope:** `src/npc/experiments/fox_causal_turn.py`,
`tests/test_fox_causal_turn.py`, `docs/architecture.md`, `docs/glossary.md`,
and this packet

**Parallel-safe with:** `None` — the code, test, and architecture comparison
must describe the same boundary.

**Durable information changed:**

- How does the system work now? -> [Architecture](../architecture.md), new
  independent actor-description seam comparison.
- What do project-specific terms mean? -> [Glossary](../glossary.md), only if
  `actor description` needs a preferred shared meaning after the boundary is
  accepted.

**Simplifier review:** Required — this task adds a candidate cross-boundary
description value and changes a single experiment module's public inputs.

## Outcome

The fox causal-turn slice exposes the smallest inspectable actor-owned input:
its epistemic profile, ordered questions, bounded proposal vocabulary, and
any actor-local retained context. The simulation-owned canonical state,
information filtering, proposal resolution, and feedback selection remain
outside that input. An architecture comparison records those ownership rules
and applies the actor-owned side to one Product-Manager-selected contrasting
actor without giving it fox cognition or access to the clearing schema.

This makes the boundary needed before shared-world composition observable
without choosing a class hierarchy, DSL, file format, registry, or general
actor framework.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Epistemic profile | [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn) and [Glossary](../glossary.md#actor-loop-terms) | Existing fox text moves from a module constant into the actor-owned description value. | Actor | Input for one turn; recorded in trace. | None |
| Actor-owned question | Same requirements and glossary section | Existing ordered fox questions move into that value unchanged. | Actor | Input for one mediation request; recorded in trace. | None |
| Bounded proposal vocabulary | Requirements: allowed `approach_food` and `wait` proposals | The description declares only the existing allowed proposal names; the simulation remains the resolver. | Actor proposes; simulation core accepts/resolves | Proposal is recorded; canonical result is committed by core. | None |
| Actor-local retained context | [Roadmap outcome 1](../roadmap.md#1-establish-the-minimal-independent-actor-description-seam) and PM acceptance recorded in this packet | Fox and foraging-crow entries explicitly use empty retained context; no memory, needs, inventory, or persistent belief state is introduced. | Actor | No runtime state or lifecycle is introduced. | None |
| Contrasting actor description | [Roadmap outcome 1](../roadmap.md#1-establish-the-minimal-independent-actor-description-seam) and PM acceptance recorded in this packet | Foraging crow: accepted profile, ordered questions, and existing `approach_food` / `wait` vocabulary below. It is documentation-only and does not establish a crow world or universal action. | Actor owns profile/questions/proposal; simulation core resolves | Comparison-only; no crow runtime state. | None |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| actor description | Proposed glossary entry, contingent on accepted implementation | Names the explicit actor-owned input shared by code, test, and architecture comparison. |
| retained context | Existing `epistemic profile` wording until a source establishes a distinct persistent value | Prevents a new state field from being implied by the description container. |

## Vision alignment

- **Vision behavior made observable:** A builder can identify the actor-owned
  inputs separately from the simulation-owned facts and rules, so a different
  actor need not traverse the simulation schema to form a proposal.
- **Classification:** `Candidate durable system foundation`
- **Reuse pressure:** The accepted foraging-crow comparison below; it need not
  execute in the fox world.
- **Boundary rejection signal:** The comparison needs a fox canonical-state
  field, filtering rule, resolver rule, or a fox-specific question-to-proposal
  policy in the contrasting actor-owned input.

## Canonical context

- [Roadmap outcome 1](../roadmap.md#1-establish-the-minimal-independent-actor-description-seam).
- [Requirements: Fox language-mediated causal turn](../requirements.md#fox-language-mediated-causal-turn).
- [Decision: natural language as the default actor-world semantic interface](../decisions.md#2026-07-26-use-natural-language-as-the-default-actor-world-semantic-interface).
- [Architecture: Fox language-mediated causal turn](../architecture.md#fox-language-mediated-causal-turn).
- Entry points: `src/npc/experiments/fox_causal_turn.py` and
  `tests/test_fox_causal_turn.py`.

## Task-specific scope

- Replace the causal-turn module's fox constants with one minimal immutable
  actor-description value or equivalent plain data input; do not add inheritance,
  a file format, loader, registry, generic actor loop, or a second runnable
  world.
- Preserve the current fox trace and its closed information boundary. The
  simulation-side renderer, resolver, canonical state, and feedback stay local
  to the simulation code.
- Add a source-variation test: changing an actor-owned profile, question set,
  or declared vocabulary changes the mediation/proposal boundary accordingly
  while the canonical state and resolver input remain simulation-owned.
- Add a withheld-fact test proving the contrasting description cannot receive
  `food_path_blocked` or another clearing-schema field through its actor-owned
  input.
- Put the ownership matrix and contrast in Architecture; do not duplicate
  behavior or rationale there.

### Accepted contrasting actor source

The Architecture comparison shall use this accepted, documentation-only actor
description:

- **Actor:** foraging crow.
- **Epistemic profile:** “You are an alert crow looking for food. You may
  assess what you can observe from above, but you do not know what lies behind
  obstacles or beyond your view. Treat sounds and smells as clues, not facts.”
- **Ordered questions:** “Do I believe the clearing is safe to enter?” then
  “Do I believe the food is worth investigating from here?”
- **Bounded proposal vocabulary:** `approach_food` (attempt to move toward
  observed food) and `wait` (take no world-changing action this turn). The
  simulation core alone accepts and resolves either proposal.
- **Retained context:** Empty. No crow memory, needs, inventory, or persistent
  belief state is introduced.

This contrast may change only actor-owned profile and question content. It
does not receive hidden facts, alter observation filtering, add a crow world,
or make `approach_food` a universal action.

## Acceptance and verification

- A causal-turn test proves the fox's existing profile, questions, allowed
  proposals, trace, resolution, and replay behavior remain unchanged.
- A source-variation test proves actor description changes affect only the
  actor-facing mediation/proposal inputs and do not alter access filtering or
  authoritative resolution.
- A withheld-fact test proves no canonical blocked-path fact crosses into the
  crow description or mediation input.
- The Architecture comparison identifies every current causal-turn element as
  actor-owned or simulation-owned and states that fox has no accepted retained
  context.
- Run the targeted causal-turn tests, `make check`, and `git diff --check`.

## Stop conditions

- No Product-Manager-selected contrasting actor description is available.
- A non-empty actor-local retained context, new proposal label, state field,
  feedback field, or question meaning lacks an accepted source, authority, or
  lifecycle.
- The smallest boundary cannot support the contrast without embedding a fox
  canonical-state field, observation filter, or resolver rule.
- Required work expands to a reusable actor framework, external mutation, or
  a change to the roadmap's priority.

## Handoff

**Status and outcome:** Ready. The Product Manager accepted the foraging-crow
comparison and explicitly selected empty retained context.

**Changed files and ownership impact:** This packet only. It records the
implementation path; no system behavior or canonical durable fact changed.

**Verification:** Read-only trace of the causal-turn implementation and tests;
no behavior changed.

**Assumptions, risks, and next action:** Treat the current fox and foraging
crow as having no retained context. Assign one Implementer to perform the
bounded refactor and comparison, then obtain Simplifier review before
acceptance.
