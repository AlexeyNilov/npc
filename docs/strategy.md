# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Strategic thesis

**Long-term capability:** A simulation builder can independently describe
simulations and heterogeneous actors, then author, run, inspect, replay, and
eventually branch scenarios in which those actors interact with a shared
authoritative simulation core.
**Confidence:** High.

The strategic proposition is that the project reaches this capability through
the smallest causally complete vertical slices. Each slice should extend the
loop between an actor and the simulation core end to end and earn its next
modular boundary through evidence. This avoids both recreating a comprehensive
framework before its boundaries are understood and allowing the first
supported actor to define the product.

The central modularity bet is the natural-language semantic boundary described
in the [vision](../README.md#vision). It belongs in the first causally complete
slice because deferring it would evidence an interface the strategy already
expects to replace. Its sufficiency for the target class of simulations must
earn broader scope through cross-scale evidence.

## Strategic horizons

| Horizon | Capability established | Unlocks |
| --- | --- | --- |
| 1. Causal closure | An actor-accessible substate and actor epistemic profile produce a recorded subjective percept; actor-owned questions inform an action proposal; the simulation core resolves and commits an authoritative outcome that becomes feedback, with a replayable causal trace. | An evidenced language-mediated boundary between actor and simulation core rather than another actor-local loop. |
| 2. Shared-world composition | Multiple heterogeneous actors receive distinct actor-accessible substates, form actor-specific percepts, and interact through time, ordering, and conflict resolution owned by the simulation core. | A credible shared-world simulation rather than a collection of isolated actor behaviours. |
| 3. Cross-scale portability | The semantic and causal contracts survive a materially different actor scale, world schema, or system context without requiring shared schema-specific sensemaking code. | A justified general capability boundary for independent scenario and actor authoring. |
| End state | Simulation builders can compose independently described simulations, heterogeneous actors, and bounded generative components in inspectable, replayable, and branchable scenarios. | The product value described in the vision. |

## Current focus

**Strategic bet:** Establish causal closure through the smallest
language-mediated boundary between an actor and the simulation core before
expanding actor cognition or designing a comprehensive engine framework.

The completed utility experiment remains foundational evidence: bounded binary
perceptions and authoritative state can produce a replayable choice without
granting the LLM authority. Its fox-local action and feedback rules do not,
however, establish an actor-accessible substate, a recorded subjective
percept, generic batched sensemaking, or an authoritative simulation core, as
its
[evidence record](evidence/2026-07-26-fox-deterministic-utility.md) makes
explicit. The fox may remain a stable test actor for Horizon 1, but further
fox-specific cognition is not the strategic objective.

The next evidence-bearing outcome should establish the complete Horizon 1
sequence: canonical state, an actor-accessible substate, a recorded subjective
percept shaped by an actor epistemic profile, batched actor-owned questions,
an action proposal, authoritative resolution, canonical transition, and
feedback. The Product Manager owns its ordering in the
[roadmap](roadmap.md#ordered-future-outcomes).

The actor-accessible substate boundary is therefore part of Horizon 1 rather
than optional infrastructure to defer: without it, the first slice would
evidence an actor-to-world interface the strategy already expects to replace.
Simulation scheduling and conflict handling remain deferred until
shared-world composition unless the first causal-closure outcome cannot be
explained or replayed without one of those responsibilities. One slice should
exercise the semantic seam without claiming portability; Horizon 3 requires
evidence from a materially different actor scale or world schema.

## Strategic constraints

- Actor loops interpret their observations and propose actions; the simulation
  core alone resolves outcomes and maintains canonical reality.
- The simulation enforces hard information-access limits before LLM mediation
  and supplies only the actor-accessible substate.
- Actors own their epistemic profiles and sensemaking questions; the engine
  owns generic mediation and orchestration, not actor- or simulation-specific
  cognition.
- Natural language is the default semantic intermediary. Subjective percepts
  and sensemaking answers are actor-local, recorded, and may be incomplete or
  distorted; they never become canonical reality merely by being generated.
- Group the questions for one percept into one sensemaking request when their
  individual answers and percept evidence can remain independently inspectable.
- An answer that informs intent identifies evidence in the recorded subjective
  percept. Missing, malformed, or unsupported answers fail closed for that
  question; percept evidence explains actor belief rather than canonical truth.
- LLM output may shape actor-local perception and sensemaking, but any output
  crossing an authoritative boundary remains a bounded proposal until the
  simulation core accepts or resolves it. Binary questions are the first
  evidenced form, not a required form for every future actor.
- Rejected perceptions and action proposals fail closed.
- Every authoritative transition remains traceable and replayable from recorded
  state, actor-accessible substate, epistemic profile, subjective percept,
  ordered questions, answers and percept evidence, submitted proposals,
  resolution decisions, and controlled variation.
- Actor-local percept and belief, canonical reality, and non-authoritative
  narration remain distinct.
- Build the smallest causally complete slice. A module need not be generic, and
  a broader abstraction requires evidence from materially different pressure.
- Current actors and experiment scaffolding do not define the product boundary.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Generative environment or Game Master authority | A PM-ordered target outcome cannot be represented by explicit resolution without embedding its domain policy in the simulation core, and bounded evidence shows generated resolution can preserve canonical validation and causal replay. |
| Structured or domain-specific cognition interface as the default | A materially different slice shows that natural language repeatedly loses action-relevant precision, cannot meet usable cost or latency, or still requires actors to depend on a shared simulation schema. |
| Richer actor-cognition-first sequencing | A named user outcome requires memory, planning, or richer sensemaking beyond epistemic profiles and actor-owned questions before the minimal boundary with the simulation core can be meaningfully assessed. |
| Application-first vertical strategy | A concrete simulation builder and problem provide stronger capability requirements than domain-neutral discovery of the simulation core. |
