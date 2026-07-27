# Roadmap

This document owns incomplete future outcomes. This document orders evidence-bearing
outcomes, not coding activities or speculative bstractions.

## 1. YAML-authored authoritative beast simulation

An author can run a minimal beast scenario defined in YAML and observe narrated
movement, eating, and fleeing in the command line. The outcome proves that
actor-specific capabilities, motivations, and ordered behavioural rules are
separate from the engine, and that scenario content can be changed without
changing engine code.

This comes first because it validates the reboot's core promise of simple,
comprehensible authoring before LLM integration adds another source of
complexity.

Dependencies and assumptions: the initial generic actor and scenario schema
must express the beast without placing beast-specific concepts in the engine.

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
