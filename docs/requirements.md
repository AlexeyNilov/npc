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
- The engine must authoritatively resolve generic movement and consumption.
  Fleeing is an actor-profile rule that proposes movement; actor rules and any
  LLM output must not alter canonical outcomes or world state.
- A command-line run must print narration for completed events so an observer
  can follow the simulation.
- An author must be able to change the actor's priorities, behavioural rules,
  perception questions, or scenario content through YAML-only changes.

### LLM-backed perception

- The system must support actor-owned, binary perception questions declared in
  YAML.
- For the first LLM perception proof, a scenario must declare the minimal
  subset of its world content visible to its actor. The engine must derive the
  actor-accessible view from that declaration; it must not rely on the LLM to
  hide inaccessible content.
- The engine must provide an actor only the world data it is allowed to know
  when obtaining answers to those questions.
- For the first proof, each questioned turn must make one non-streaming request
  containing the full declared question list and the derived accessible view.
  The response must be a JSON object with exactly those question texts as keys
  and JSON booleans as values; a standalone `json` Markdown code fence around
  that object is accepted.
- LLM answers may inform an actor's behavioural rules, but the LLM must not
  decide canonical outcomes, change mechanics, or alter authoritative world
  state.
- For the first LLM perception proof, if the LLM is unavailable, or its
  response is malformed, incomplete, or contains a non-binary answer, the run
  must fail fast with a diagnostic perception error. It must not select,
  resolve, or commit a proposal for the failed turn.

### Observer inspection and narration

- For a resolved turn, the observer must be able to distinguish the actor's
  declared perception questions and validated answers, and its attempted
  choice, from the authoritative
  accepted or rejected outcome.
- The CLI must render that inspection record as deterministic labelled
  `perception`, `choice`, and `authoritative outcome` sections for every
  resolved turn. The record, rather than narration, must establish the
  validated answers, attempted proposal, and acceptance or rejection.
- The system must generate entertaining non-authoritative narration only after
  authoritative resolution. Its input must be limited to completed
  presentation facts, and it must not become action-selection input or alter
  canonical state.
- A narration failure after resolution must not undo or hide the completed
  outcome. The observer must still receive the authoritative outcome and an
  explicit indication that narration was unavailable.

### Explicitly out of scope for the first proof

- Deterministic replay from a fixed seed is not required.
