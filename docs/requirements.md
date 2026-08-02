# Requirements

This document owns observable high level system behavior. Do not put experimental stuff here.

## Enduring authoring boundaries

- An actor profile must be authored separately from a scenario so an author can
  reference the same profile from more than one scenario without duplicating
  its actor-specific behaviour.
- Actor-specific concepts and rules must be defined in the actor YAML profile,
  not embedded in the simulation engine.
- Scenarios must define participating actor profiles, initial conditions, and
  world content separately from actor-specific behaviour.
- An author must be able to change the actor's priorities, behavioural rules,
  perception questions, or scenario content through YAML-only changes.

## Language-mediated actor decisions

- The system must support actor-owned, binary perception questions declared in
  YAML.
- The engine must provide an actor only the world data it is allowed to know
  when obtaining answers to those questions.
- Language-model output may inform an actor's proposal, but it must not decide
  canonical outcomes, change mechanics, or alter authoritative world state.
- Only validated model output may cross the mediation boundary into actor
  decision-making.
- The simulation engine must authoritatively validate and resolve actor
  proposals and remain the sole authority for canonical state transitions.

## Observer inspection and narration

- The observer must be able to distinguish an actor's available information,
  questions and validated answers, and attempted proposal from the
  authoritative outcome.
- The system must generate entertaining non-authoritative narration only after
  authoritative resolution. Its input must be limited to completed
  presentation facts, and it must not become action-selection input or alter
  canonical state.
- A narration failure after resolution must not undo or hide the completed
  outcome.
