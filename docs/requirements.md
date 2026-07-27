# Requirements

This document owns observable system behavior.

## Actual requirements

### First reboot proof

The system must demonstrate that an author can define an actor and a scenario
entirely in YAML, without changing engine code to change actor-specific
behaviour or scenario content.

- An actor profile must define its capabilities, motivations, ordered
  condition-to-action behavioural rules, and binary perception questions.
- An actor profile must be authored separately from a scenario so an author can
  reference the same profile from more than one scenario without duplicating
  its actor-specific behaviour.
- Actor-specific concepts and rules must be defined in the actor YAML profile,
  not embedded in the simulation engine.
- A scenario must define the world content relevant to the first proof,
  including food and threats or threat events.
- The engine must authoritatively resolve movement, eating, and fleeing. Actor
  rules and any LLM output must not alter canonical outcomes or world state.
- A command-line run must print narration for completed events so an observer
  can follow the simulation.
- An author must be able to change the actor's priorities, behavioural rules,
  perception questions, or scenario content through YAML-only changes.

### LLM-backed perception

- The system must support actor-owned, binary perception questions declared in
  YAML.
- The engine must provide an actor only the world data it is allowed to know
  when obtaining answers to those questions.
- LLM answers may inform an actor's behavioural rules, but the LLM must not
  decide canonical outcomes, change mechanics, or alter authoritative world
  state.

### Explicitly out of scope for the first proof

- Deterministic replay from a fixed seed is not required.
