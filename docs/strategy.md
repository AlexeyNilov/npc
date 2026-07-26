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

**Status:** Accepted.

**Long-term capability:** Turn the evidenced actor/simulation-core boundary into
a composition capability through which the
[simulation builder](glossary.md#product-roles-and-components) can supply and
replace independently owned simulations and actors, then extend composed
scenarios through stateful execution and causal branching until the
[product vision](../README.md#vision) is reachable.

**Confidence:** Medium. The completed causal-closure and shared-world slices,
plus one bounded organisational allocation test, support the semantic and
authority boundaries under materially contrasting pressure. They do not
establish an independently usable composition surface, a reusable simulation
runtime, persistent multi-step execution, branching, or usable live-model cost
and latency.

The strategic proposition is to move from boundary discovery to product-shaped
composition before expanding engine breadth. A thin builder-facing seam creates
direct user value, forces simulation and actor ownership to remain independent,
and gives later temporal and branching semantics a real authored scenario to
serve. It is more reversible than standardising a general scheduler, world
model, or branch representation first.

Each horizon remains a smallest causally complete vertical capability. The
completed experiment modules are evidence for the boundary, not components that
must be generalised or a claim that the end-state engine already exists.

## Strategic horizons

| Horizon | Capability established | Unlocks |
| --- | --- | --- |
| 1. Builder-controlled composition | A simulation builder can supply an independently owned simulation description and heterogeneous actor descriptions to a common causal execution boundary, then run, inspect, and replay one bounded shared-world scenario without modifying generic engine machinery or introducing schema-specific cognition into it. A compatible actor or simulation rule-set replacement remains local to its supplied component and composition declaration. | The first product-shaped authoring surface and stable builder-input, compatibility, authority, trace, replay, and replacement contracts for later horizons. |
| 2. Stateful shared-world execution | A composed scenario advances through multiple authoritative steps with explicit time, ordering, conflict resolution, feedback, and retained context while preserving information boundaries and causal replay. | Meaningful evolving scenarios and stable points from which alternatives can be explored. |
| 3. Causal branching | A builder can branch a recorded scenario at a selected point, vary bounded source inputs or controlled generative inputs, and inspect comparable outcomes while preserving branch lineage and replayable authoritative causality. | Counterfactual exploration without surrendering causal inspection. |
| End state | Builders can compose and replace independently described simulations, heterogeneous actors, and bounded generative components in inspectable, replayable, and branchable scenarios without domain-specific changes to generic engine machinery. | The product value described in the vision. |

The dependency order is strict: Horizon 1 establishes the authored inputs,
authority boundary, and trace/replay contract; Horizon 2 carries those contracts
through time; Horizon 3 branches only recorded states whose causal history can
already be replayed.

## Current focus

**Strategic bet:** Establish builder-controlled composition before designing a
general temporal runtime or branch model.

The outcomes in the prior discovery sequence are complete: the current
[roadmap state](roadmap.md#product-frame) records causal closure, actor
description, shared-world interaction, and a contrasting allocation slice, and
the [portability evidence](evidence/2026-07-26-village-rationing-portability.md)
supports retaining natural language as the default semantic interface within
its stated limits. Those results are sufficient to change the capability
sequence, not to claim general portability. The next sequence-changing
uncertainty is whether a builder can use the boundary without the engine or
actors absorbing one scenario's schema and policy.

The next evidence-bearing outcome should therefore demonstrate one thin,
causally complete authoring-to-run path: independently supplied simulation and
actor descriptions compose into a bounded shared-world run whose authoritative
result can be inspected and replayed. It should establish only the minimum
reusable boundary required by that builder outcome; code deduplication alone is
not evidence of a product capability. The Product Manager owns the exact
outcome and its ordering in the
[roadmap](roadmap.md#ordered-future-outcomes).

A multi-step temporal model remains deferred to Horizon 2. A Horizon-1 slice may
declare the bounded ordering or conflict rule needed to close its run; pull
forward reusable temporal semantics only when that builder outcome cannot be
causally complete without them.

### Target modular composition model

**Target, not a current implementation claim:** The product is a composition
system with four independently owned responsibilities. Independence means that
a component can be replaced through its declared contracts without changing
generic engine machinery or unrelated components. It does not mean zero
coupling, zero domain-authoring work, or separate deployment processes.

| Responsibility | Owns | Boundary |
| --- | --- | --- |
| Builder | Supplies or selects simulation and actor descriptions, makes their compatibility explicit, and runs, inspects, replays, and eventually branches the composition. | Chooses compatible meaning-bearing components without encoding their policy in engine defaults. |
| Actor, including an agent-backed actor | Owns its description, epistemic profile, questions, retained context, subjective cognition, bounded proposal vocabulary, and proposal selection. | Consumes only its filtered observation and feedback; it neither reads canonical reality directly nor determines a proposal's canonical effect. |
| Simulation | Supplies the domain authority: canonical facts and their meanings, actor-specific observation filtering, admissible proposal semantics, resolution and conflict rules, canonical transitions, and feedback selection. | Owns world meaning and policy without absorbing actor cognition or generic orchestration. |
| Engine | Provides the composition and execution environment. Its generic machinery mediates and sequences exchanges, isolates actor channels, validates contract structure and authority paths, and records and replays causality. At runtime it hosts or invokes the builder-supplied simulation authority as the authoritative simulation core within the engine. | Enforces the protocol without interpreting world fields, deciding domain validity, or inventing actor or simulation meaning. |

```text
Builder composes:
Simulation description ↔ Engine ↔ Actor descriptions

Runtime exchange managed and recorded by the engine:
simulation-filtered observation → actor cognition → bounded proposal
    → simulation-owned resolution and canonical transition
    → actor-specific feedback
```

As defined in the
[glossary](glossary.md#product-roles-and-components), a simulation description
must carry or identify the capabilities that own domain authority; it is not
assumed to be passive data. This model does not yet choose whether a supplied
component uses code, configuration, a domain-specific language, or an external
process. Natural language remains the default on the perception and sensemaking
side, while anything crossing into simulation authority remains a bounded
proposal. The engine understands the causal roles and contract envelopes, not
what a blocked path, food reserve, priority rule, or other world-specific term
means.

The Product Manager should define the builder-visible meaning of independent
supply and compatibility, and the run, inspection, and replay outcome that
demonstrates them. The Technical Lead should choose the minimum API, data shape,
orchestration, validation, persistence, and verification for that outcome,
escalating any new public meaning or irreversible interface choice.

## Strategic constraints

These are capability-level requirements for any eventual authoring interface,
runtime contract, or adapter. They constrain the product without selecting a
concrete API or data shape; observable acceptance behavior remains owned by
[Requirements](requirements.md).

- Independently supplied actor and simulation descriptions must be identifiable
  and recordable with the run. The builder makes their compatibility explicit;
  the engine does not repair semantic mismatches by inventing domain adapters,
  actor policy, or world meaning.
- Replacing an actor implementation or description or a simulation rule set
  changes only the supplied component and its composition declaration. It must
  not require domain-specific edits to generic engine machinery or unrelated
  actors. New domain semantics may still require localized authoring in the
  simulation or actor that owns them.
- Composition deliberately couples observation, proposal, resolution, and
  feedback semantics. At minimum, the builder pairs an actor-declared bounded
  proposal vocabulary with simulation-declared accepted proposals; no fixed or
  parameter-free vocabulary is presumed universal.
- The simulation enforces semantic information-access rules and supplies only
  each actor's accessible substate. The engine enforces channel and recipient
  isolation so actors cannot bypass that projection; it cannot infer whether
  domain-specific filtering is semantically correct.
- Actor loops interpret observations and propose actions. Proposals remain
  untrusted requests; the simulation core alone applies domain admissibility and
  resolution rules, commits outcomes, and maintains canonical reality.
- Generic engine validation may reject malformed envelopes, undeclared
  pairings, missing results, or unauthorized transition paths. Only the
  simulation may decide domain questions such as preconditions, resource
  sufficiency, conflicts, transition effects, or feedback meaning.
- Natural language remains the default semantic intermediary. Subjective
  percepts, beliefs, and sensemaking answers are actor-local, recorded, and may
  be incomplete or distorted; they never become canonical merely by being
  generated.
- Questions about one percept may share a mediation request only while each
  answer and its percept evidence remain independently inspectable. Missing,
  malformed, or unsupported mediation results cannot authorize a proposal or
  canonical change.
- Any model or generative output that may affect the world remains a bounded
  proposal until the simulation core validates or resolves it.
- Actor-local cognition, canonical reality, and non-authoritative narration
  remain distinct.
- Every authoritative transition retains enough source context, boundary
  exchanges, resolution decisions, and controlled variation to remain
  inspectable and replayable.
- Every branch identifies its parent point and bounded change; branch lineage
  never substitutes for replay evidence within either resulting run.
- Build the smallest causally complete slice. Reuse is earned by a builder
  outcome across material pressure, not by similarity between experiment
  implementations. Current actors, scenario policy, and fixtures do not define
  the product boundary.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Temporal-runtime-first sequencing | A builder-controlled causal slice cannot expose a coherent composition boundary until a specific multi-step ordering, timing, or conflict responsibility is established. Pull forward only that named responsibility, not a comprehensive runtime. |
| Branching before reusable composition | A named builder's primary outcome is counterfactual comparison, and a bounded branch over an existing trace can test that value without fixing a premature general branch or scenario model. |
| Further disposable cross-domain boundary discovery | A composition attempt shows that the semantic or authority contracts fail under a material new pressure, rather than merely exposing missing reusable orchestration. |
| Structured or domain-specific cognition as the default | A target builder outcome shows that natural language repeatedly loses action-relevant precision, cannot meet usable cost or latency, or requires actors to share simulation-schema traversal logic. |
| Application-first vertical strategy | A concrete simulation builder and problem provide stronger capability requirements than the current domain-neutral path, or repeated composition attempts cannot produce useful builder value without application-specific engine or schema coupling. |
| Generative environment or Game Master authority | A target outcome cannot be represented by explicit resolution without embedding its domain policy in the core, and bounded evidence shows generated resolution can preserve canonical validation and causal replay. |
| Universal engine-interpreted world or rule model | Repeated builder-controlled compositions show stable world and rule semantics across materially different simulations, and component-supplied rules cannot provide usable authoring, validation, inspection, or replay without a shared representation. Standardise only the common meaning supported by that evidence. |
