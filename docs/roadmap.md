# Roadmap

This document owns incomplete future outcomes. The Product Manager adds and
orders those outcomes; during completion reconciliation, the Technical Lead may
remove only the exact outcome verified as complete. The Technical Lead does not
add, replace, or reorder outcomes. This document orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Target user:** a simulation builder who needs independently described
simulations and heterogeneous actors with flexible behaviour, while retaining
causal inspection, replay, and eventual branching. The canonical target and
value are in the [Vision](../README.md#vision).

**Current roadmap state:** The completed fox causal-closure, actor-description,
and shared-world slices established the actor/core boundary in one clearing-and-
trap world. The completed village-rationing portability experiment then tested
that boundary in a materially different organisational allocation context. Its
[evidence record](evidence/2026-07-26-village-rationing-portability.md) supports
retaining natural language as the default semantic interface through that
contrasting slice, within its recorded limits.

The completed [stateful shared-world execution evidence](evidence/2026-07-26-stateful-shared-world-execution.md)
shows that the composition boundary can carry one bounded scenario through two
authoritative steps with actor-local context and replay. The ordered
Horizon-3 outcome below tests whether that recorded history can support one
bounded, causally inspectable alternative; it does not infer a general branch
model from the completed stateful-execution experiment.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 1. Bounded causal branching of a recorded shared-world scenario

**Type:** Bounded experiment for the Horizon 3 decision.

**Evidence and assumptions:** The completed
[stateful shared-world execution evidence](evidence/2026-07-26-stateful-shared-world-execution.md)
establishes one replayable, two-step causal history with authoritative state,
actor-specific context, and resolution records. It does not establish whether a
builder can vary a committed past while retaining explicit lineage, simulation
authority, actor-channel isolation, and causal replay. This outcome assumes
that the existing composed clearing declaration and its recorded two-step
history are sufficient starting context; it does not assume a reusable branch
or temporal model.

**Target user and desired observable outcome:** A simulation builder selects
the recorded initial source state—the parent point before ordinal step one—of
the two-step clearing history and declares the sole bounded variation:
simulation-owned `trap_materials_ready` changes from `true` in the parent to
`false` in the alternative. Its established clearing meaning is owned by the
supplied simulation: materials are unavailable, so a trap cannot be set. Both
outcomes make the selected parent point, the declared source difference, their
resulting authoritative histories, and replay results inspectable. The
alternative does not overwrite, reinterpret, or silently inherit authority
from the parent.

This deliberately uses the recorded initial source state as a valid parent
point. It does not branch after step one or introduce a variation that changes
a committed trap outcome, because either would require a new clearing
transition and authority decision.

**Decision unlocked:** Whether the two-step composition boundary can support
the minimum causal-branching capability, or whether preserving comparable
lineage and replay requires a strategic revision before Horizon 3 proceeds.

**Options and counterfactual next actions:**

- **Supported:** A bounded alternative preserves explicit parent-point and
  variation provenance; both parent and alternative replay their own
  authoritative histories without actor mediation, and simulation authority
  and actor isolation remain intact. Treat the causal-branching slice as
  evidence for Horizon 3 and ask the Product Strategist to select the next
  capability outcome.
- **Rejected:** Establishing the alternative requires engine interpretation of
  clearing meaning, lets a variation bypass simulation resolution, leaks actor
  channels, cannot replay either history independently, or requires a general
  temporal or branch representation. Escalate to the Product Strategist to
  reconsider the capability sequence or constraints; do not promote a general
  branch model.
- **Inconclusive:** The fixture creates two final outputs but cannot expose the
  selected parent point, bounded difference, independent replay, or comparison
  provenance. Do not claim Horizon 3; identify the missing observable evidence
  before ordering another outcome.

**Signals and stop rule:** Support requires an inspectable parent and
alternative with a declared parent point and bounded variation, replay evidence
for each authoritative history without new mediation, and trace mutations that
reject changed lineage, variation, or authoritative records. Stop and escalate
before generalizing if the smallest scenario needs a scheduler, persistence,
universal clock, generic conflict representation, universal branch schema, or
new domain/authority decision. Ordinary delivery verification cannot resolve
this question because successful branching mechanics alone would not show that
the causal relationship and authority boundary remain intelligible to the
builder; the cost of prematurely standardising those semantics is greater than
this one bounded comparison.

**Constraints and exclusions:** Preserve the strategic constraints on
simulation-owned authority, bounded proposals, actor-channel isolation, and
recorded controlled variation. Do not add an unbounded execution loop,
persistence, a general scheduler, a universal temporal/branch model,
engine-interpreted clearing policy, or live-model cost and latency claims.
