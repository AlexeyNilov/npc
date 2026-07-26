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

**Current roadmap focus:** establish
[Horizon 1 causal closure](strategy.md#strategic-horizons) through the smallest
language-mediated boundary between an actor and the authoritative simulation
core. The simulation supplies an actor-accessible substate; the actor supplies
its epistemic profile and questions; generic LLM mediation records a subjective
percept and evaluates the actor-owned questions in one request while retaining
each answer and its percept evidence separately; and the simulation core
resolves a bounded action proposal, commits the outcome, and returns feedback
with a replayable causal trace.

The current fox [architecture](architecture.md) and completed
[utility evidence](evidence/2026-07-26-fox-deterministic-utility.md) remain
foundational inputs, not the product frame. The capability path and constraints
are owned by [Strategy](strategy.md).

## Ordered future outcomes

### 1. Establish one language-mediated causally closed actor turn

**Strategic horizon:** 1 — causal closure.

**Plain-language goal:** Make one actor turn into a complete, inspectable
conversation between an actor and a world. The actor can form a belief and try
something; only the simulation decides what really happens.

**Illustrative fox example (non-binding):** The world knows that a hunter is
nearby and food is behind a wall. It may tell the fox only that it hears
footsteps and smells food. A wary, hungry fox interprets those observations,
asks whether it is safe to approach and whether food is likely nearby, then
proposes `flee` or `approach`. The world resolves that proposal—for example,
the wall prevents reaching the food—and records both what the fox believed and
what actually happened. The fox's belief never becomes a world fact merely
because it was generated.

**Why this is next:** The accepted product model and strategy require this
boundary before more fox-local cognition, scheduling, or a reusable framework.
The completed fox utility work establishes a useful authority constraint, but
does not establish the actor-to-simulation-core boundary.

**Target user and problem:** A simulation builder needs one independently
described actor to interpret only what the simulation permits it to know and
attempt an action without that interpretation becoming canonical reality.

**Desired observable outcome:** In one bounded scenario, a developer can
inspect and replay a complete turn in which:

- the simulation core starts from canonical state and deterministically derives
  the actor-accessible substate before any LLM request;
- the actor supplies its own epistemic profile and two or more ordered,
  actor-owned questions;
- generic mediation produces one recorded subjective percept and evaluates the
  questions in one request, while retaining each answer and the percept
  evidence that supports it separately;
- the actor converts those answers into a bounded action proposal; and
- the simulation core, rather than the actor or model, resolves the proposal,
  commits the canonical transition, and returns authoritative feedback.

The recorded trace must be sufficient to reproduce the authoritative
transition from its initial state, actor-accessible substate, epistemic
profile, percept, ordered questions, answers and evidence, proposal,
resolution, and any controlled variation. Missing, malformed, or unsupported
answers and rejected percepts must fail closed without becoming canonical
facts.

**Constraints:** Preserve the strategic authority and information-boundary
constraints. This is one small vertical slice, not a claim that the fox schema,
its utility policy, or its current sensors are reusable engine interfaces.
Non-authoritative rendering may remain outside the turn unless it is needed to
inspect the causal trace.

**Ordinary completion evidence:** A checked-in scenario and replay exercise
the whole sequence; tests demonstrate the hard information boundary, separate
answer/evidence retention, failure-closed behavior, authoritative resolution,
and reproduction of the committed transition. This is delivery rather than an
experiment: the target behavior and authority boundary are already decided,
and ordinary verification can establish whether the slice meets them.

**Decision unlocked:** Whether the same bounded semantic and causal contracts
can support a minimal independently described actor boundary, or whether a
concrete failure requires escalation to the Product Strategist because it
conflicts with the target model or strategic constraints.

### 2. Establish the minimal independent actor-description seam

**Strategic horizon:** Bridge from 1 to 2. **Depends on:** outcome 1.

**Plain-language goal:** Make explicit what belongs to an actor, so a future
simulation builder can describe a different actor without teaching that actor
the world's internal schema or recreating the engine's rules.

**Illustrative fox example (non-binding):** A fox description could say that
it is cautious and hungry, what kinds of observations it can interpret, which
questions it asks, that it may propose `flee`, `approach`, or `wait`, and which
actor-local feedback matters on its next turn. It must not contain hidden world
facts, decide whether an action succeeds, or encode the hunter's rules.

**Target user and problem:** A simulation builder needs to describe an actor's
own viewpoint and possible attempts independently. Otherwise, each new actor
will become coupled to the first simulation's data structure and resolution
logic, undermining the intended product model before composition is tested.

**Desired observable outcome:** The first causal-closure slice yields an
explicit boundary that distinguishes actor-owned epistemic profile, questions,
proposal vocabulary, and actor-local retained context from simulation-owned
canonical state, information filtering, action resolution, and feedback
selection. A contrasting actor description can be stated against that boundary
without inheriting fox-specific cognition or traversing the simulation schema.

**Constraints:** Do not select a class hierarchy, DSL, file format, registry,
or general actor framework merely to make the boundary look reusable. The
smallest expression that makes ownership and coupling inspectable is enough;
the Technical Lead selects its technical form. Any accepted consequential
rationale belongs in [Decisions](decisions.md), not this roadmap.

**Ordinary completion evidence:** A documented comparison identifies which
elements of the causal-closure actor are actor-owned and which are
simulation-owned, and a second contrasting actor can be described using the
former without adding shared schema-specific sensemaking logic. This is direct
delivery and review, not an experiment: it makes a decided product boundary
explicit before it is multiplied across a shared world.

**Decision unlocked:** Whether the independent actor boundary is sufficiently
clear to compose two actors in one authoritative world, or whether a concrete
coupling pressure warrants a Product Strategist decision before doing so.

### 3. Compose a shared authoritative world for heterogeneous actors

**Strategic horizon:** 2 — shared-world composition. **Depends on:** outcome
2.

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

### 4. Test cross-scale portability of the semantic and causal contracts

**Strategic horizon:** 3 — cross-scale portability. **Depends on:** outcome
3.

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
