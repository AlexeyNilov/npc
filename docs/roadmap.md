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

The next ordered outcome is Builder-controlled composition. It turns the
completed boundary evidence into a builder-facing capability; no later outcome
is ordered until its result determines whether the path can proceed to
stateful execution.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 1. Builder-controlled composition

**Outcome:** The project developer, acting as a simulation builder, can choose
a supplied world-and-rules component and supplied actor components, declare
that they belong together, and run one bounded shared-world scenario. The
builder can inspect what each actor was shown and proposed, how the simulation
resolved those proposals, and the resulting world state; replaying that record
makes the same authoritative result without new mediation. The record names
the participating supplied components and the builder's compatibility
declaration. The engine gives actionable, provenance-preserving diagnostics
for structural contract failures, while semantic compatibility and domain
validity remain respectively builder- and simulation-owned.

**Builder workflow:** The builder names the supplied actors and simulation
rules, makes one readable composition declaration that pairs their proposals,
and validates it before running. A structurally ready composition can be run,
inspected, and replayed from its record. A structurally invalid one identifies
the relevant component and declaration problem—for example, an actor proposal
that the simulation has not paired—without attempting a semantic diagnosis.
For either replacement run, the builder changes only the named component in
that declaration and then runs and compares the resulting records. The
builder must be able to complete this flow without understanding generic engine
internals or locating scenario-specific orchestration code. This describes the
required user experience, not a required CLI, GUI, configuration format, or
API.

The builder can demonstrate the composition in three separately inspectable
runs: a baseline; an actor-only substitution with the simulation, generic
engine machinery, and unrelated actors unchanged; and a simulation rule-set
substitution with the actors and generic engine machinery unchanged. Each
substitution is selected through the composition surface, is local to the
supplied component and its declaration, and produces an observable difference
in cognition, proposal, resolution, feedback, or authoritative outcome. A
rule-set substitution changes authoritative rule definition, rather than only
initial state or a parameter.

**Illustrative example (non-binding):** The builder composes a fox actor, a
hunter actor, and supplied clearing-and-trap rules. In the baseline run, the
hunter sets a trap, the fox approaches food, and the rules resolve the fox as
caught. In the actor-variant run, the builder substitutes a more cautious fox
while retaining the hunter, rules, and engine; that fox may wait instead. In
the rule-variant run, the builder retains the original actors but substitutes
rules that resolve the fox's proposal before the hunter's trap-setting
proposal; the fox can reach the food before a trap is set. The trace for each
run shows the supplied components, actor observations and proposals,
simulation decisions, feedback, and final result; each trace replays to that
same result. For example, if an actor declares an action the simulation has
not paired with it, the engine identifies that structural mismatch and its
components, rather than attempting to decide what the action means in the
clearing.

**Why now:** Completed causal-boundary and village-rationing portability
evidence support the independent authority and natural-language boundaries,
but do not show that a builder can compose or replace supplied components
without scenario-specific engine coupling. This outcome is the first
product-shaped authoring surface required by Strategy Horizon 1.

**Decision unlocked:** Whether the demonstrated builder-facing composition,
compatibility, replacement, trace, and replay boundary is sufficient to carry
through time into Horizon 2, or whether observed composition failures require
the Product Strategist to reconsider the capability sequence or constraints.
