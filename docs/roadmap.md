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

**Current roadmap focus:** make the independent actor-description seam explicit
before composing multiple actors. The completed fox causal-closure slice
established the smallest language-mediated boundary between an actor and the
authoritative simulation core: simulation-filtered observation, actor-owned
epistemic profile and questions, one recorded subjective percept with separate
answers and evidence, bounded proposal, authoritative resolution, feedback,
and replayable causal trace. The next outcome identifies which of those
elements belong to an independently described actor rather than to the fox
scenario or simulation core.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 2. Compose a shared authoritative world for heterogeneous actors

**Strategic horizon:** 2 — shared-world composition. **Depends on:** outcome
1.

**Plain-language goal:** Let different actors act in the same world while
keeping their knowledge, beliefs, and decisions separate. The simulation acts
as the referee when their actions interact.

**Illustrative fox example (non-binding):** A fox smells food while a hunter
hears movement. The fox gets only fox-appropriate observations and the hunter
gets only hunter-appropriate observations. Each forms its own percept and
proposes an action: the fox approaches; the hunter sets a trap. The simulation
decides the order and outcome, such as whether the fox arrives before the trap
is ready, and records why that authoritative result occurred.

**Target user and problem:** A simulation builder needs actors with different
information access and interpretation to affect one shared reality, rather
than running isolated actor loops that merely resemble a simulation.

**Desired observable outcome:** A bounded scenario contains at least two
heterogeneous actors. For a common canonical state, the simulation gives each
actor only its own actor-accessible substate; each forms and records its own
percept and answers; and each submits bounded proposals. The simulation core
owns time, ordering, conflict resolution, and committed transitions. The
resulting trace makes clear which observations, proposals, resolution decisions
and feedback caused each authoritative change, and replay reproduces that
sequence.

**Constraints:** Actor percepts, beliefs, and narration remain actor-local and
non-authoritative. Actors must not share simulation-schema-specific sensemaking
code merely to participate. Do not generalize scheduling or conflict machinery
beyond what the bounded scenario needs.

**Ordinary completion evidence:** A checked-in contention or ordering case
demonstrates distinct actor-accessible substates, distinct recorded percepts,
authoritative ordering and resolution, and reproducible canonical results.

**Decision unlocked:** Whether the semantic boundary is credible for a shared
world and should be tested across a materially different scale or schema, or
whether observed composition pressure calls for a strategy decision about the
core contracts.

### 3. Test cross-scale portability of the semantic and causal contracts

**Strategic horizon:** 3 — cross-scale portability. **Depends on:** outcome
2.

**Plain-language goal:** Check that the same actor/world approach works for a
meaningfully different kind of simulation—not just a larger fox scenario.

**Illustrative comparison (non-binding):** After demonstrating a fox and
hunter world, apply the same boundaries to a village organisation deciding how
to ration food, a fleet responding to disruptions, or another materially
different context selected during planning. Each actor should still receive a
limited view, form its own interpretation, make a bounded proposal, and leave
the simulation to decide the real outcome.

This is an experiment, not routine delivery, because one successful
single-scale shared-world slice cannot establish whether natural-language
mediation preserves actor independence across a materially different actor
scale, world schema, or system context.

**Decision and options:** Decide whether to retain natural language as the
default actor-world semantic interface for the next capability expansion, or to
reconsider a structured supplementary/replacement interface or a narrower
product scope. The comparison scenario must differ materially from the
Horizon-2 actor scale, world schema, or system context; selecting that scenario
is part of planning, not an assumption that the current fox domain is
representative.

**Hypothesis:** The actor-accessible-substate, epistemic-profile, subjective-
percept, actor-owned-question, bounded-proposal, and authoritative-resolution
contracts can support the contrasting scenario without shared
schema-specific sensemaking code while retaining inspectable, replayable
authoritative causality.

**Support signal and next action:** The contrasting slice preserves the hard
information boundary, separate actor-local records, bounded authoritative
resolution, and causal replay without actor cognition traversing a shared world
schema. Retain the language-default strategy and use the evidence to guide the
next product capability.

**Rejection signal and next action:** The slice repeatedly loses
action-relevant precision, cannot meet usable cost or latency, or requires
shared schema-specific sensemaking logic to work. Escalate the observed limit
to the Product Strategist for a decision between a structured supplement,
replacement interface, or a narrower target scope; do not silently preserve
the default.

**Stop rule:** Evaluate only the established shared-world slice and one
materially contrasting slice, with the same required causal-trace inspection
and replay checks. Stop once the evidence distinguishes the two decision
options; do not add a general framework or extra domains merely to strengthen a
preferred conclusion.

**Why an experiment is warranted:** Existing fox and first shared-world
evidence can verify their own slices but cannot resolve portability. Being
wrong would either entrench an interface that forces schema coupling or impose
unnecessary structure on heterogeneous actors; a bounded contrasting slice is
cheaper than either commitment.
