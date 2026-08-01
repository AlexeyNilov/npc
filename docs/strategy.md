# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Capabilities not yet demonstrated

The completed beast proof establishes a bounded authoritative simulation,
LLM-mediated binary perception, and inspectable post-resolution narration. It
does not yet demonstrate the broader engine promised by the vision. The
capability path must still establish, in a deliberate dependency order:

- interaction among multiple actors, including groups, organisations, and
  non-human systems;
- actor scheduling and interaction mechanics;
- reusable scenario and actor-profile authoring, rather than the bounded proof
  schema and world model;
- a general sensing or visibility model, rather than explicitly listed visible
  entity IDs;
- subjective state, memory, persistence, and replay where they are needed for
  the product;
- general actions, map topology, and event-log facilities where they are
  needed for the product;
- actor choice in which motivations have defined effects beyond YAML rule
  ordering; and
- narration reliability or truthfulness beyond its constrained,
  post-resolution input boundary.

These are capability gaps, not a committed backlog. The roadmap should select
only the smallest next outcome that delivers value or resolves a dependency
blocking further value.
