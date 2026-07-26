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

**Long-term capability:** A simulation builder can author, run, inspect, replay,
and eventually branch scenarios in which heterogeneous actor loops operate
within a shared authoritative simulation substrate.
**Confidence:** Medium.

The strategic proposition is that the project reaches this capability through
the smallest causally complete vertical slices. Each slice should extend the
actor-to-substrate loop end to end and earn its next modular boundary through
evidence. This avoids both recreating a comprehensive framework before its
boundaries are understood and allowing the first supported actor to define the
product.

The accepted pivot and its rationale are in
[Decisions](decisions.md#2026-07-26-center-the-product-on-a-modular-authoritative-simulation-engine);
the durable meaning of determinism is recorded
[separately](decisions.md#2026-07-26-define-determinism-as-replayable-authoritative-causality).

## Strategic horizons

| Horizon | Capability established | Unlocks |
| --- | --- | --- |
| 1. Causal closure | An actor receives an observation and proposes an action; the substrate resolves and commits an authoritative outcome that becomes feedback, with a replayable causal trace. | An evidenced actor-to-substrate boundary rather than another actor-local loop. |
| 2. Shared-world composition | Multiple heterogeneous actors receive actor-specific observations and interact through substrate-owned time, ordering, and conflict resolution. | A credible simulation kernel rather than a collection of isolated actor behaviours. |
| 3. Cross-scale portability | The causal contracts survive a materially different actor scale or system context without requiring one shared cognition model. | A justified general capability boundary for scenario authoring and branching. |
| End state | Simulation builders can compose heterogeneous actors and bounded generative components in inspectable, replayable, and branchable scenarios. | The product value described in the vision. |

## Current focus

**Strategic bet:** Establish causal closure at the smallest actor-to-substrate
boundary before expanding actor cognition or designing a comprehensive engine
framework.

The completed utility experiment remains foundational evidence: bounded binary
perceptions and authoritative state can produce a replayable choice without
granting the LLM authority. Its fox-local action and feedback rules do not,
however, establish a substrate that owns world outcomes, as its
[evidence record](evidence/2026-07-26-fox-deterministic-utility.md) makes
explicit. The fox may remain a stable test actor for Horizon 1, but further
fox-specific cognition is not the strategic objective.

The next evidence-bearing outcome should establish the proposal, resolution,
authoritative transition, and feedback boundary named by Horizon 1. The Product
Manager owns its ordering in the [roadmap](roadmap.md#ordered-future-outcomes).

**Strategic discovery:** Decide whether Horizon 1 requires only canonical state,
proposal, resolution, commitment, and feedback, or whether actor-specific
observation projection and simulation time or ordering are prerequisites for
causal closure. Compare the earlier
[LLM-system domain model](https://github.com/AlexeyNilov/llm_system/blob/main/doc/domain_guide.md)
with an environment-owned
[agent cycle](https://pettingzoo.farama.org/main/api/aec/), an
[event-owned clock](https://simpy.readthedocs.io/en/4.1.0/api_reference/simpy.core.html),
and [generative Game Master authority](https://github.com/google-deepmind/concordia).

If the minimal boundary can explain and replay the Product Manager's first
causal-closure outcome, defer observation infrastructure, scheduling, and
conflict handling until their named horizons. If it cannot, bring only the
responsibility needed to explain that failure into Horizon 1. If explicit
resolution itself prevents the required outcome, test the reconsideration
trigger below. Stop the comparison when its sequencing decision and rationale
are accepted in [Decisions](decisions.md); do not maintain a framework
catalogue.

## Strategic constraints

- Actor loops interpret their observations and propose actions; the substrate
  alone resolves outcomes and maintains canonical reality.
- LLM output remains a bounded, verifiable proposal until accepted by an
  authoritative boundary. Binary questions are the first evidenced perception
  form, not a required form for every future role.
- Rejected perceptions and action proposals fail closed.
- Every authoritative transition remains traceable and replayable from recorded
  state, ordered inputs, submitted proposals, resolution decisions, and
  controlled variation.
- Actor-local belief, canonical reality, and non-authoritative narration remain
  distinct.
- Build the smallest causally complete slice. A module need not be generic, and
  a broader abstraction requires evidence from materially different pressure.
- Current actors and experiment scaffolding do not define the product boundary.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Generative environment or Game Master authority | A PM-ordered target outcome cannot be represented by explicit resolution without embedding its domain policy in the substrate, and bounded evidence shows generated resolution can preserve canonical validation and causal replay. |
| Actor-cognition-first sequencing | A named user outcome requires memory, planning, or richer sensemaking before the minimal substrate boundary can be meaningfully assessed. |
| Application-first vertical strategy | A concrete simulation builder and problem provide stronger capability requirements than domain-neutral substrate discovery. |
