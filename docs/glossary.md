# Glossary

This document owns the meanings and preferred names of project-specific terms.
It prevents terminology drift; it does **not** own observable behavior, current
mechanisms, rationale, or experiment results. Those remain with their canonical
owners and are linked below.

## Adding and using terms

Consult this document when a project-specific term is ambiguous, crosses a
documentation or code boundary, or is proposed for reuse. Do not preload it for
unrelated work.

Add or change an entry only when an accepted term needs one preferred project
meaning across more than one packet, boundary, or durable document. Keep
experiment-local or disposable names local unless they become shared. A glossary
entry standardizes a name; it does not authorize new state, behavior, a
threshold, or a product decision. Record those facts with their canonical
owners, then link to them here.

## Authority and state

**Authoritative.** Data, rules, or transitions that the simulation is permitted
  to use to constrain or advance canonical reality. In the current fox
  experiments, starting distance, starting hunger, selected action, and their
  deterministic transitions are authoritative. Generated output does not
  become authoritative merely by being produced; an authoritative boundary
  must validate or resolve it for its permitted use.

**Canonical reality.** The authoritative actor and world facts accepted by the
  simulation at a point in its causal history. Actors may receive different
  observations of that reality. The current experiments have only fox-local
  authoritative inputs and state, not a reusable canonical world model.

**Simulation substrate.** The target engine boundary that maintains canonical
  reality, resolves actor action proposals, commits outcomes, and returns
  feedback. It is a strategic capability, not a claim that the current fox code
  already provides a reusable substrate. See the
  [strategy](strategy.md#strategic-horizons).

**Controlled variation.** An explicit stochastic or generative input whose
  request, result, and place in the causal trace are recorded. It may influence
  a proposal or an authoritative rule only through its declared boundary; it
  is not implicit model output or unrecorded randomness.

**Canonical turn.** The completed, authoritative `TurnTrace` passed to presentation. Rendering
  preserves it by value and cannot modify it. See the [current rendering
  design](architecture.md#non-authoritative-rendering-of-completed-fox-outcomes).

**Feedback.** Information from a resolved outcome that informs later perception
  or sensemaking. Authoritative feedback may include committed state used by a
  later turn. Current fox feedback is resulting distance and, for the utility
  experiment, resulting hunger.

**Outcome.** The authoritative result of resolving an action proposal against
  canonical reality. In the current fox loop it is the result of executing a
  selected action. It is established before feedback and optional narration.

**Persistent need state.** An authoritative actor-local state retained across turns and used by policy.
  `hunger` is the current experiment's only such state; it is not a general
  need system.

## Actor-loop terms

**Actor loop.** The target model `authoritative reality → actor-specific
  perception → sensemaking → intent → action proposal → substrate resolution →
  outcome and canonical transition → feedback`, with feedback informing later
  perception and sensemaking. It is a product target, not a claim that the
  current fox code is a reusable engine abstraction. See the
  [vision](../README.md#vision).

**Reality.** Preferred short form for canonical reality when discussing the
  actor loop. In the current fox utility loop, the inputs treated as facts for
  one turn are a player-message string plus authoritative distance and hunger.

**Perception.** Actor-specific information proposed or derived from reality.
  Current perception is an LLM-backed, action-relevant proposal about one
  player message and remains untrusted until deterministic validation accepts
  it.

**Sensemaking.** The actor-local interpretation of perceptions into decision
  context. Current fox sensemaking is limited to deterministic acceptance or
  rejection of sensor candidates; rejected perceptions contribute no utility.

**Intent.** An actor's selected commitment about what it wants to attempt.
  Current fox intent is the deterministic policy stage that selects an action
  from accepted perceptions and authoritative state; it is called `choice` in
  current traces.

**Action proposal.** A bounded operation an actor wants to attempt. It does not
  determine its own success or canonical effect; the simulation substrate owns
  resolution. Current fox actions are selected and executed within one
  fox-local boundary and do not yet establish this separation.

**Action.** The operation represented by an action proposal or, in the current
  fox experiments, a selected deterministic operation. Current fox actions are
  `flee`, `approach`, and `do_nothing`; their exact transitions belong to the
  [requirements](requirements.md).

**Causal closure.** A complete actor-to-substrate sequence in which an actor
  receives an observation, proposes an action, the substrate resolves and
  commits its outcome, and the resulting reality becomes feedback with a
  replayable causal trace. It is the first strategic horizon, not a current
  implementation claim.

## Perception and validation

**Sensor.** A narrow LLM-backed function that proposes one binary fact. The current
sensors are the threat sensor and explicit-food-offer sensor; a sensor does
not choose an action.

**Candidate.** The structured boolean, certainty, and evidence proposed by a sensor before
validation. A raw candidate is the unparsed model response; a parsed candidate
has the expected structure but is still untrusted.

**Grounded evidence.** For a `true` candidate, one non-empty verbatim substring of the player
message that supports the asserted fact. Missing or absent evidence rejects
the candidate.

**Certainty.** The candidate's finite numeric value from 0 through 1. It is validated for
the perception contract but is trace-only: it does not alter policy, utility,
or action.

**Fail closed.** Treat malformed, ambiguous, invalid, or ungrounded perception
  output as unaccepted, so it has no effect on action selection. A rejected
  action proposal makes no unauthorized canonical transition, although its
  recorded rejection may become feedback.

**Hearing gate.** The deterministic reachability check that permits sensor calls only when the
fox's starting distance is within the current hearing range. A skipped sensor
call is distinct from a rejected candidate.

**Threat.** The current sensor's binary assessment that a player message contains a
credible hostile threat toward the named creature.

**Explicit food offer.** The current sensor's binary assessment that a player message explicitly
offers food to the named creature. It does not establish food reachability or
consumption.

## Policy and presentation

**Utility.** An experiment-local numeric score for a candidate action, calculated only
from accepted perceptions and authoritative hunger. It is not a general utility
model. See [utility experiment evidence](evidence/2026-07-26-fox-deterministic-utility.md).

**Tie order.** The fixed, deterministic priority used when actions have equal utility. The
current utility experiment orders `flee`, then `approach`, then `do_nothing`.

**Non-authoritative narration.** Player-facing text generated only after a canonical turn completes. It may
expressively describe supplied presentation facts, but never selects an action,
changes world state, or becomes later-turn input.

**Narrator / renderer.** The injectable function that produces non-authoritative narration from a
completed-action prompt. “Narrator” is the player-facing name; “renderer” is
the code-level interface name.

**Fallback narration.** The deterministic text returned when narration is blank, oversized,
unavailable, or raises an exception. It leaves the canonical turn unchanged.

## Experiment boundaries and evidence

**Fox-local.** Scoped to the current fox experiment and deliberately not evidence of a
reusable actor, state, movement, utility, or presentation framework.

**Scenario corpus.** The checked-in YAML collection of fixed inputs and LLM fixture completions
used to reproduce an experiment.

**Fixture.** A deterministic test or corpus substitute for an external dependency, such
as an LLM completion or narrator.

**Trace.** A structured, JSON-safe record of one turn or rendering attempt. It supports
inspection and replay of the experiment; it is not itself world state.

**Disposable scaffolding.** Experiment-specific wrappers, corpora, trace types, constants, or adapters
that support learning but are not yet candidates for reuse.

**Replayable / reproducible.** Recorded initial state, ordered inputs, submitted
  proposals, resolution decisions, and controlled variation reproduce the same
  authoritative transition sequence. Current experiments achieve this with
  fixed corpora and deterministic rules. Replay does not require regenerated
  presentation prose to be identical or all future actor behaviour to be
  predictable.
