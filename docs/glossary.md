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

## Product roles and components

**Simulation builder.** Preferred short form **builder** only when the product
  context is clear. The intended product-user role responsible for supplying
  and composing simulation descriptions and actor descriptions.

**Observer.** The immediate user of an autonomous simulation application. A
  launched observer session advances without observer input.

**Simulation Engine.** It provides execution environment for simulations and actors. 
  It contains the authoritative simulation core and supplies generic mediation,
  orchestration, and causal recording around it. Generic engine machinery does
  not invent simulation-specific policy or actor cognition; it enforces and
  coordinates their declared boundaries.

**Authoritative simulation core.** Preferred short form **simulation core**.
  The target component within the simulation engine that maintains canonical reality,
  resolves actor action proposals, commits outcomes, and returns feedback. It
  is distinct from actor cognition, generic LLM mediation, and presentation.

## Actor-loop terms

**Actor loop.** The target model `authoritative reality → actor-accessible
  substate plus its epistemic profile → subjective percept → actor-owned
  questions and sensemaking → intent → action proposal → authoritative
  resolution → outcome and canonical transition → feedback`, with feedback
  informing later perception and sensemaking.

**Actor-accessible view.** The simulation-filtered part of canonical reality
  that an actor is permitted to receive for one observation. The simulation
  enforces this hard information boundary before generative mediation; an LLM
  is not responsible for hiding facts outside it.

**Actor profile.** Actor-supplied context that shapes subjective perception,
  including sensory limitations, knowledge, worldview, biases, and relevant
  current context. It remains actor-local and does not alter canonical reality.

**Sensemaking.** The actor-local interpretation of perceptions into decision context.

**Actor-owned question.** A sensemaking question defined by an actor and
  evaluated only against that actor-accessible view. The engine may batch
  multiple questions into one LLM request without taking ownership of their
  meaning or combining their individual answers and percept evidence.

**Intent.** An actor's selected commitment about what it wants to attempt.

**Action proposal.** A bounded operation an actor wants to attempt. It does not
  determine its own success or canonical effect; the authoritative simulation
  core owns resolution.

## Perception and validation

**Sensor.** A narrow LLM-backed function that proposes one binary fact. 
For example a threat sensor or explicit-food-offer sensor; a sensor does
not choose an action.

**Candidate.** The structured boolean and evidence proposed by a sensor before
validation. A raw candidate is the unparsed model response; a parsed candidate
has the expected structure but is still untrusted.

## Presentation

**Non-authoritative narration.** Observer-facing text generated only after a canonical turn completes. It may
expressively describe supplied presentation facts, but never selects an action,
changes world state, or becomes later-turn input.
