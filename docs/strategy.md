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

**Long-term capability:** Reach the
[product vision](../README.md#vision) through applications that prove the
actor/simulation boundary creates valuable experiences, then extract only the
composition and runtime capabilities that recur under that application
pressure.

**Confidence:** Medium in the authority and causal-inspection boundary; low in
observer value. The completed composition, two-step execution, and fixed
alternative slices show that supplied actors and simulation rules can remain
separate while authoritative outcomes stay inspectable and replayable. They do
not show that the result is fun, meaningful, independently usable, or worth
turning into a general platform.

The strategic proposition is application first: build one small, complete
observer-facing simulation before expanding engine breadth. The simulation must
hold attention through autonomous change, differently informed actors,
comprehensible consequences, and an unfolding causal history. Scenario-local
code is acceptable; reusable machinery is earned only when a successful
application needs it more than once.

This is a reversible sequencing choice, not a change to the README vision or a
commitment that the observer simulation is the final product. The accepted
rationale is in
[Decisions](decisions.md#2026-07-26-run-the-clearing-as-an-autonomous-observer-simulation).

## Strategic horizons

| Horizon | Capability established | Unlocks |
| --- | --- | --- |
| 1. Complete observer application | An observer can watch one short autonomous simulation in which recorded simulation events change the shared world, differently informed actors react, and the resulting causal history remains understandable and exactly replayable. | The first direct evidence that the engine boundary can produce a coherent experience without user intervention. |
| 2. Evidenced observer value | A bounded simulation sustains curiosity, anticipation, causal comprehension, and interest in another run at usable pacing and reliability. | Evidence for which event, actor, state, presentation, and content capabilities deserve further investment. |
| 3. Application-earned composition | A second materially different application or scenario can reuse the boundaries proven by the observer simulation without domain-specific changes to generic machinery. Only responsibilities that recur across successful application work become builder-facing capabilities. | A credible path from one application to the simulation-builder product without guessing a platform in advance. |
| End state | The modular, inspectable simulation-building capability described in the [vision](../README.md#vision), shaped by proven applications rather than theoretical completeness. | Durable builder value grounded in demonstrated observer and authoring needs. |

The dependency order is strict: complete an autonomous simulation before
judging its observer value; establish value before extracting a platform;
generalise only behavior that survives materially different application
pressure. Persistent execution, branching, broad authoring tools, and other
engine breadth are not independent horizons unless a proven user outcome makes
them necessary.

## Current focus

**Strategic bet:** Use the existing clearing boundary to deliver and evaluate a
small autonomous observer simulation before doing more platform work.

The current developer remains the
[simulation builder](glossary.md#product-roles-and-components); the immediate
application user is an
[observer](glossary.md#product-roles-and-components). The clearing is a
low-cost validation vehicle because its fox, hunter, partial-information
boundary, authoritative rules, and causal record already exist. Those fixtures
constrain what has been evidenced, not what the eventual product must contain.

The target observer loop is:

```text
understand the starting situation → a recorded simulation event occurs
    → differently informed actors perceive and respond
    → see the simulation resolve consequences
    → understand what happened → anticipate what may follow
```

The next ordered outcomes are one complete short session followed by a bounded
observer-value evaluation. Their observer-visible scope, exclusions, evidence,
and decision gates belong to the
[roadmap](roadmap.md#ordered-future-outcomes).

The engine is internal technology during this horizon. A scenario may use
fixed-duration sequencing, a bounded event vocabulary, scenario-owned random
selection, and explicit content. Each event selection is
[controlled variation](glossary.md#authority-and-state): its place and result
are recorded before the simulation applies any canonical effect. Observer
controls such as start, pause, inspection, replay, and restart never enter the
causal history.

A fresh restart may produce a new recorded event history; exact replay consumes
the recorded history without fresh randomness or actor mediation. Do not add
persistence, arbitrary scheduling, branching, a general randomness or
variation framework, a scenario editor, a plugin system, or a universal world
schema unless the observer outcome cannot be complete without one of those
named capabilities.

### Target modular composition model

**Target, not a current implementation claim:** The application adds an
observer experience around the existing composition responsibilities. Component
independence still means replacement through declared contracts without
domain-specific changes to generic engine machinery or unrelated components;
it does not require zero coupling or a public authoring surface during this
horizon.

| Responsibility | Owns | Boundary |
| --- | --- | --- |
| Observer | Watches the session and may control presentation through start, pause, inspection, replay, or restart. | Supplies no event, actor proposal, simulation rule, or other causal input during a run. |
| Builder and application | Supplies the simulation and actors; owns the scenario declaration, initial setup, observer framing, presentation, and component compatibility. | The project developer may author these directly while the builder-facing product surface remains unselected. |
| Actor, including an agent-backed actor | Owns its description, epistemic profile, questions, retained context, subjective cognition, bounded proposal vocabulary, and proposal selection. | Consumes only its filtered observation and feedback; it neither reads canonical reality directly nor determines a proposal's canonical effect. |
| Simulation | Supplies the domain authority: canonical facts and event meanings, event policy and effects, actor-specific observation filtering, admissible proposal semantics, resolution and conflict rules, canonical transitions, and feedback selection. | Owns world meaning and policy without absorbing actor cognition or generic orchestration; only it may make a selected event authoritative. |
| Engine | Provides the composition and execution environment. Its generic machinery sequences exchanges, isolates actor channels, records controlled variation, validates authority paths, and records and replays causality. At runtime it hosts or invokes the builder-supplied simulation authority as the authoritative simulation core within the engine. | Enforces the protocol without interpreting world fields, selecting domain event meaning, deciding domain validity, or inventing actor or simulation policy. |

```text
Builder supplies simulation + actors + initial setup
                          ↓
recorded controlled event → simulation-owned canonical effect
                          ↓
simulation-filtered observation → actor cognition → bounded proposal
                          ↓
simulation resolution and transition → actor feedback

Observer ← presentation of the recorded event, reactions, and consequences
```

As defined in the
[glossary](glossary.md#product-roles-and-components), a simulation description
must carry or identify the capabilities that own domain authority; it is not
assumed to be passive data. The observer application does not select whether a
later supplied component uses code, configuration, a domain-specific language,
or an external process. Natural language remains the default on the perception
and sensemaking side while it remains precise, responsive, and affordable
enough for observation. Anything from an actor or generative component that may
affect the world crosses into simulation authority as a bounded proposal.

## Strategic constraints

These rules constrain every application and any later reusable engine surface.
Observable behavior remains owned by
[Requirements](requirements.md).

- Observer value outranks engine completeness. Work on generic machinery only
  when a named observer outcome cannot be complete without it.
- The observer supplies no causal input. Viewing controls may change
  presentation or select a fresh run, but they cannot alter the canonical
  history of a run already in progress.
- The simulation alone owns canonical facts, information-access rules,
  event meaning and effects, admissibility, resolution, transitions, and
  authoritative feedback. Actors receive only their filtered inputs and cannot
  commit world changes.
- Random or generative events are controlled variation, never ambient
  authority. Record each selected event and its causal position before the
  simulation validates or commits its effects; exact replay introduces no new
  randomness.
- Actor cognition and model output remain local and untrusted. Anything that
  may affect the world is a bounded proposal until the simulation resolves it;
  non-authoritative narration remains separate from both.
- Observer-facing consequences must remain causally inspectable. Retain enough
  source state, actor exchanges, simulation decisions, and resulting state to
  explain and replay authoritative outcomes.
- Natural-language mediation must earn its place through action-relevant
  precision, understandable behavior, usable pacing, and acceptable operating
  cost. Deterministic or structured behavior is preferable where mediation
  does not improve the experience.
- Scenario-local rules, content, sequencing, and presentation are permitted.
  Do not extract a general scheduler, state model, compatibility system, or
  authoring surface from one observer simulation.
- A restartable short session is the default. Persistence, branching, and
  comparison are separate capabilities that require their own demonstrated
  observer or builder value.
- Build the smallest complete experience. More actors, turns, content, and
  interfaces are justified by observed observer needs, not by theoretical
  engine breadth.

## Reconsideration

| Alternative not chosen now | Reconsider when |
| --- | --- |
| Builder-platform-first sequencing | A concrete external builder job provides stronger value evidence than the observer simulation, or successful application work repeatedly needs the same authoring capability. |
| General temporal runtime or persistence | A validated observer loop cannot deliver its required session length, continuity, or return-to-view outcome with bounded scenario-owned sequencing. Pull forward only the missing responsibility. |
| Branching or counterfactual comparison | Observers or builders need to compare alternatives from the same recorded history and restart/replay cannot satisfy that job. |
| Interactive player agency | Observer evidence and an explicit user decision show that watching alone cannot deliver the intended value and that causal intervention is preferable to another autonomous application. Do not add intervention merely as an engagement patch. |
| A different application vertical | The bounded clearing evaluation rejects its curiosity, comprehension, or consequence proposition after one focused correction, while the authority boundary itself remains credible. |
| Structured cognition as the default | Model-mediated actors repeatedly lose action-relevant precision, make consequences feel arbitrary, or cannot meet usable pacing or cost. |
| Make the observer simulation the product | Repeated observer evidence is stronger than evidence for a builder product and the user explicitly accepts changing the README vision and target user. |
