# Roadmap

This document owns incomplete future outcomes. The Product Manager adds and
orders those outcomes; during completion reconciliation, the Technical Lead may
remove only the exact outcome verified as complete. The Technical Lead does not
add, replace, or reorder outcomes. This document orders evidence-bearing
outcomes, not coding activities or speculative engine abstractions.

## Product frame

**Long-term target user:** A simulation builder who needs heterogeneous actors
and inspectable, replayable causality. The canonical target and value remain in
the [Vision](../README.md#vision).

**Immediate application user:** An
[observer](glossary.md#product-roles-and-components) watching a small
autonomous clearing simulation. The project developer remains the current
builder. This application-first sequence tests the engine through observation;
it does not yet change the README target user or commit to the observer
simulation as the final product.

**Current roadmap state:** The completed
[composition](evidence/2026-07-26-builder-controlled-composition.md),
[stateful execution](evidence/2026-07-26-stateful-shared-world-execution.md),
and [fixed alternative](evidence/2026-07-26-bounded-causal-branching.md)
slices support bounded actor/simulation ownership, partial information,
authoritative resolution, retained state, trace, and replay. The
[builder guide](builder-guide.md) explicitly remains a deterministic
developer-facing experiment rather than an observer experience or general
framework. No evidence yet shows that an observer finds this boundary
compelling, meaningful, clear, or worth watching again.

The accepted direction is therefore to deliver one complete autonomous
clearing session and then evaluate its observer value. The capability sequence
belongs to
[Strategy](strategy.md); the rationale belongs to
[Decisions](decisions.md#2026-07-26-run-the-clearing-as-an-autonomous-observer-simulation).

## Ordered future outcomes

### 1. Deliver one complete autonomous clearing session

**Type:** Direct delivery.

**Target user and problem:** A first-time observer currently has experiments
and an interactive fox demonstration, but no complete autonomous simulation
with a readable premise, unfolding events, actor reactions, retained
consequences, and an ending.

**Desired outcome:** An observer can start one short fixed-length clearing
session without editing code or a composition declaration. Once started, the
session advances without any observer input entering canonical reality. During
the session:

- the simulation selects a bounded random event through recorded controlled
  variation and alone decides its canonical meaning and effects;
- the fox and hunter receive only their own simulation-filtered information
  and retained context, then form bounded reaction proposals;
- the simulation alone resolves actor proposals, commits state, and selects
  authoritative feedback;
- each simulation-committed event and simulation-resolved actor proposal may
  change what happens later in the same session;
- the observer receives a concise presentation and can inspect a readable
  causal account that distinguishes the selected event, each actor's
  interpretation and attempted action, authoritative resolution, and resulting
  state; and
- the session reaches a clear ending, explains what happened, and permits exact
  replay or a fresh run.

Start, pause, inspection, replay, and restart are presentation controls. They
must not become event choices, actor proposals, simulation rules, random
sources, or other causal inputs.

**Working experience proposition:** The observer watches a fox and hunter
navigate a changing clearing and becomes curious about how limited information,
random events, and retained consequences will shape the outcome. This is an
explicit product assumption to test, not established user evidence.

**Illustrative only:** Events might alter food availability, trap readiness,
weather, sound, scent, or tracks. Exact event meanings, selection policy, turn
count, terminal conditions, and actor policies must first be accepted as
observable behavior in [Requirements](requirements.md); these examples are not
binding mechanics.

**Evidence and assumptions:**

- The clearing composition already demonstrates separate fox and hunter
  inputs, bounded proposals, simulation-owned resolution, local actor and rules
  substitutions, trace, and replay.
- The exact-two-step slice demonstrates one committed state change and
  actor-local retained context. It does not provide an autonomous event loop.
- The accepted definition of
  [controlled variation](glossary.md#authority-and-state) permits recorded
  stochastic input without weakening authoritative replay. It does not provide
  a general event or randomness framework.
- The interactive fox demonstration provides a configured model path and
  non-authoritative narration. Its player messages remain a separate supported
  demonstration and are not simulation events for this application.
- The central assumptions are that autonomous change can hold attention, two
  differently informed actors are enough for the first session, and the
  existing clearing meanings can support a comprehensible arc.

**Scope boundaries:**

- Deliver one scenario, one observer role, the fox, the hunter, one bounded
  event vocabulary, and only the turns, state, and endings needed for a
  complete session.
- An observer-facing terminal, graphical, or web surface is an implementation
  choice; raw JSON or source edits alone are not an observer experience.
- A fresh run may select a different event history. Each selected event, its
  causal position, and its authoritative effect must be recorded. Exact replay
  uses that recorded history and introduces no fresh randomness.
- Model-mediated perception, sensemaking, or narration may be used only through
  the existing authority constraints. The session must retain an explicit,
  viewable failure or fallback path when model output is unavailable,
  malformed, or unusable.
- Scenario-owned fixed sequencing is sufficient. Do not add arbitrary
  scheduling, a universal time model, save persistence, branching, alternative
  comparison, an interactive player role, a general event or randomness
  framework, a scenario editor, a plugin system, multiplayer, or a second
  scenario.
- Scenario-local implementation is acceptable. Reuse and architectural
  generality are not completion criteria.

**Completion evidence:** Ordinary delivery verification must show a complete
start-to-ending path, at least one selected event that changes canonical state
or an actor-visible input, materially different reactions under at least two
recorded event histories, actor-information isolation, simulation-only
canonical transitions, an observer-readable causal account, fallback behavior,
and clean restart. Replay verification must reproduce the authoritative
history without fresh event selection or actor mediation and reject a changed,
missing, or reordered recorded event.

A human acceptance pass must watch the session from its normal entry point,
inspect its explanation, replay it exactly, and start a fresh run without
editing code or supplying a causal choice. This outcome makes no claim that the
simulation is compelling.

**Decision unlocked:** Whether the application is coherent and reliable enough
to expose to first-time observers for the value experiment below. If completing
the session requires a general platform or randomness capability, stop and
return that named dependency to Product Strategy rather than broadening the
engine silently.

### 2. Evaluate whether autonomous clearing observation is compelling and meaningful

**Type:** Decision-oriented discovery after Outcome 1.

**Decision and options:** Decide whether to deepen this observer simulation,
revise or replace its core application concept, or stop application investment
and reconsider the product path.

**Hypothesis:** A short autonomous clearing session in which recorded random
events affect differently informed actors will give first-time observers
curiosity about what happens next, at least one meaningful and causally fair
consequence, and a specific reason to inspect, replay, or watch another run.

**Why discovery is required:** Automated tests and developer acceptance can
establish correctness, authority, and causal explanation. They cannot establish
curiosity, emotional consequence, perceived meaning, clarity, or desire to keep
watching. The cost of one small evaluation is low compared with building more
content or extracting a platform around an unvalued simulation.

**Smallest evaluation:** Observe one exploratory round with three to five
people who did not implement the simulation. Each receives only the normal
observer-facing introduction, watches one session without coaching when
possible, and may inspect, replay, or start another run voluntarily. Record:

- whether the observer can state the premise and understand that they have no
  causal role;
- where events, actor reactions, or consequences become confusing;
- whether the observer anticipates a development or asks a concrete question
  about what may happen next;
- whether the observer can explain one complete
  event-to-observation-to-reaction-to-resolution-to-state chain;
- which event or consequence felt most meaningful and why;
- whether a surprise felt causally fair after inspection;
- whether model behavior, latency, or fallback disrupted the experience; and
- whether the observer chooses exact replay, starts another run, or names a
  different outcome they want to witness.

This is qualitative directional evidence, not market validation.

**Support signals:**

- A repeated pattern across observers shows that they follow the session,
  understand their noncausal role, and can explain why its ending occurred.
- Observers show anticipation or spontaneous curiosity about an actor, event,
  or possible consequence before the session ends.
- Observers identify at least one meaningful consequence produced by the
  interaction of a random event, actor-limited information, and authoritative
  resolution.
- Multiple observers voluntarily inspect, replay, start another run, or
  describe a concrete different outcome they would like to witness.
- Inspection makes an initially surprising consequence clearer rather than
  exposing arbitrary or contradictory behavior.

**Rejection signals:**

- Observation feels passive without generating curiosity, anticipation, or
  attachment to an outcome.
- Random events feel disconnected from actor reactions or authoritative
  consequences.
- Outcomes remain arbitrary or confusing after the causal account is shown.
- The fox and hunter's separate perspectives add no perceived value to the
  unfolding simulation.
- Observers complete the session but cannot name a meaningful event,
  consequence, or reason to keep watching.
- Model-mediated behavior repeatedly damages trust, clarity, or pacing enough
  to dominate the experience.

**Inconclusive conditions:** Entry-point defects, unclear instructions,
crashes, unavailable model infrastructure, or a single obvious presentation
problem prevent observers from experiencing the core loop. Correct at most one
clearly local blocker and repeat the same evaluation; do not add content or
engine capabilities to rescue an inconclusive result.

**Stop rule:** Stop after the first usable three-to-five-observer round, or
after one permitted blocker correction and repeat. Do not extend the scenario,
increase the cast, or build a general event/runtime framework before recording
the result.

**Counterfactual next actions:**

- **Supported:** Order the smallest outcome that deepens the specific source of
  observer value demonstrated. Do not assume that means more engine generality.
- **Mixed but actionable:** Revise one named weakness in event pacing,
  presentation, causal explanation, or actor behavior and repeat the same
  hypothesis.
- **Rejected because of the clearing concept:** Stop expanding this observer
  simulation and select a different concrete application vertical; retain only
  the engine boundaries supported by prior evidence.
- **Rejected because of model mediation:** Preserve the observer loop if it has
  value, but replace or supplement the affected cognition with bounded
  structured or deterministic behavior before another evaluation.
- **Rejected at the application level:** Return to Product Strategy to compare
  another application against builder-first discovery rather than continuing
  platform extraction by default.

No outcome after this decision is ordered. Persistence, branching, broader
content, and a builder-facing surface remain deferred until the recorded result
identifies an observer or builder job that requires them.
