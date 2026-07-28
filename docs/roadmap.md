# Roadmap

This document owns ordered evidence-bearing outcomes, including completed
milestones retained with their completion evidence. It does not own coding
activities or speculative abstractions.

## 1. YAML-authored authoritative beast simulation

**Status:** Completed

An observer can run a minimal beast scenario defined in YAML and observe narrated
movement, eating, and fleeing in the command line. The outcome proves that
actor-specific capabilities, motivations, and ordered behavioural rules are
separate from the engine, and that scenario content can be changed without
changing engine code.

This comes first because it validates the reboot's core promise of simple,
comprehensible authoring before LLM integration adds another source of
complexity.

Dependencies and assumptions: the initial generic actor and scenario schema
must express the beast without placing beast-specific concepts in the engine.

### Delivery plan and completion evidence

1. Establish the smallest YAML description that can express scenario state,
   an actor profile, ordered behavioural rules, and bounded action proposals.
2. Run that description deterministically from the command line: a rule selects
   a proposal, the engine resolves it, commits the canonical transition, and
   narrates the completed event.
3. Demonstrate a single beast trace covering fleeing from a threat, moving
   toward reachable food, and eating it once reachable. This trace is
   illustrative, not a binding scenario design.
4. Demonstrate YAML-only variation: changing rule order changes the selected
   proposal when food and threat coincide, and changing scenario content changes
   behaviour without engine changes.

Completion evidence shows authoritative resolution and narration for movement,
eating, and fleeing, including rejection of invalid and unsupported proposals.
It also shows that the engine contains no beast-specific policy. Verification:
`make check` and the 9 behavioural tests pass.

Motivations are actor-profile labels in this proof. The result does not show
that motivations independently rank or alter a choice; ordered rules resolve
the demonstrated conflict.

### Run the first proof

After installing development dependencies, run:

```text
.venv/bin/python -m npc scenarios/beast.yaml
```

The command prints the deterministic beast trace. The scenario supplies
canonical initial state and references `actors/beast.yaml`; that profile owns
the beast's ordered rules, capabilities, and motivations. The one-dimensional
location model and YAML document shapes are disposable scaffolding for this
milestone, not a public scenario schema.

### Considerations and boundaries

- This outcome proves one actor and one minimal scenario, not a general
  multi-actor framework or a reusable game model.
- Do not introduce LLM calls, subjective-perception evaluation, generated
  flavour narration, or replay guarantees here. They belong to later outcomes
  or are explicitly out of scope.
- An actor profile may declare binary `perception_questions` for compatibility
  with outcome 2, but outcome 1 does not evaluate them or require an LLM.

## 2. YAML-declared LLM perception for the beast

The same actor profile can declare small binary perception questions. The LLM
answers those questions from the actor-accessible world data, and the actor's
existing behavioural rules use the answers. Canonical world transitions remain
the engine's responsibility.

This follows the authoritative simulation because the perception layer needs a
legible world state, actor boundary, and action-resolution loop to mediate.

Dependency: outcome 1. The LLM's role remains limited to perception; it does
not decide actions or outcomes.

## 3. Inspectable subjective and authoritative event narration

The command-line observer can distinguish completed canonical events from the
actor's declared perception and resulting choice. This makes the value of the
LLM perception layer inspectable in a running scenario.

This follows LLM perception because there must be an actor-specific subjective
view to inspect.

Dependency: outcome 2.
