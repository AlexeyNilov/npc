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

No incomplete outcome is currently ordered. A later Product Manager decision
must add the next evidence-bearing outcome; this roadmap does not infer one
from the completed experiment.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 1. Builder-controlled composition

**Outcome:** The project developer, acting as a simulation builder, can declare
one bounded shared-world composition from independently supplied simulation and
heterogeneous actor descriptions; run it; inspect its authoritative causal
record; and replay it without new mediation. The composition records the
participating supplied components and the builder's declared compatibility.
The engine gives actionable, provenance-preserving diagnostics for structural
contract failures, while semantic compatibility and domain-validity judgments
remain respectively builder- and simulation-owned.

The builder can demonstrate the composition in three separately inspectable
runs: a baseline; an actor-only substitution with the simulation, generic
engine machinery, and unrelated actors unchanged; and a simulation rule-set
substitution with the actors and generic engine machinery unchanged. Each
substitution is selected through the composition surface, is local to the
supplied component and its declaration, and produces an observable difference
in cognition, proposal, resolution, feedback, or authoritative outcome. A
rule-set substitution changes authoritative rule definition, rather than only
initial state or a parameter.

**Why now:** Completed causal-boundary and village-rationing portability
evidence support the independent authority and natural-language boundaries,
but do not show that a builder can compose or replace supplied components
without scenario-specific engine coupling. This outcome is the first
product-shaped authoring surface required by Strategy Horizon 1.

**Decision unlocked:** Whether the demonstrated builder-facing composition,
compatibility, replacement, trace, and replay boundary is sufficient to carry
through time into Horizon 2, or whether observed composition failures require
the Product Strategist to reconsider the capability sequence or constraints.
