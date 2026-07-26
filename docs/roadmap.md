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

The next ordered outcome is Stateful shared-world execution. It carries the
completed builder-controlled composition boundary through time; no later
outcome is ordered until its result determines whether recorded multi-step
state is a sufficient base for causal branching.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 1. Stateful shared-world execution

**Outcome:** The project developer, acting as a simulation builder, can run one
already composed shared-world scenario through exactly two authoritative steps.
Each step starts from the canonical state committed by the prior step, has an
explicit ordinal, gives every actor only its simulation-filtered current input
and its own retained context, collects bounded proposals, and resolves them
under a simulation-declared order and conflict rule. The simulation alone
commits the resulting state and selects actor-specific feedback; the engine
preserves channel isolation, sequences the declared exchanges, and records the
causal history without interpreting world meaning.

The builder can inspect one timeline containing both steps: each step's source
state, actor-visible inputs and retained context, proposals, resolution order
and decisions, canonical transitions, feedback, and resulting state. Replaying
the timeline from its initial state reproduces both authoritative steps without
new mediation. A changed recorded state, context, boundary exchange, decision,
or transition is rejected rather than silently producing a different history.

**Illustrative example (non-binding):** The builder runs the supplied fox,
hunter, and clearing rules for two steps. In step one, the hunter sets the
trap while the fox waits; the committed state records that the trap is set and
each actor receives only its own feedback. In step two, the actors receive
their own retained context and new simulation-filtered views of that committed
world. If the fox approaches, the already-set trap catches it. The builder can
inspect why the same action has a different result at each point in the
timeline, then replay both steps without asking either actor to mediate again.

**Scope:** This establishes only a bounded two-step execution and its causal
record. It does not choose a general scheduler, unbounded persistence, a
universal time or conflict representation, a branch model, or a domain schema.
The Technical Lead chooses the smallest implementation that makes the
builder-visible timeline and replay outcome real.

**Why now:** The completed composition evidence shows that a builder can supply,
inspect, replay, and separately replace the components of one bounded
shared-world run. The next unresolved product question is whether those
ownership, isolation, and replay contracts survive a committed state change
and a subsequent actor exchange.

**Decision unlocked:** Whether a recorded multi-step causal history is stable
enough to support Horizon 3 causal branching, or whether observed problems in
time, ordering, conflict resolution, feedback, or retained context require the
Product Strategist to revise the capability sequence or constraints.
