# Strategy

This document owns the answer to: **How do we reach the product vision
coherently?** It records the current vision-to-capability path: the product
model, strategic constraints, capability dependencies, and the few material
unknowns that could change that path.

It is not a task backlog or an implementation design. The [README](../README.md)
owns the vision, the [roadmap](roadmap.md) owns ordered incomplete next outcomes,
and [decisions](decisions.md) owns the rationale for accepted consequential
choices. Link to those owners rather than copying their contents.

## Product direction

The bounded beast and trader demonstrations are sufficient evidence for the
project to begin platform construction. They are disposable scaffolding: retain
them only while they help build the replacement, then remove them with their
proof-specific code and tests. They are no longer the delivery model for
deciding whether to build the product.

The product should now be assembled as a modular simulation engine. Build
reusable seams around canonical world execution, actor access and cognition,
and inspection before expanding domain mechanics. Preserve the demonstrated
boundaries, but do not generalize either proof's beast movement, offers,
visibility list, or YAML shapes as a platform contract.

The platform is a shared execution and inspection foundation, not a game. A
game or simulation composes the platform with its own world model, state,
rules, action/resolution modules, access policy, and actor profiles. The first
property-board game is one such application: it depends on the platform, while
the platform must remain independent of property-board concepts. Later games
and simulations use the same composition boundary rather than inherit or
modify that application's mechanics.

## Platform capabilities to establish

The completed beast proof and trader-offer proof establish bounded authoritative
simulations with LLM-mediated binary assessments, constrained actor proposals,
and inspectable resolution. The trader proof additionally shows ordered state
feedback and one observed intent-linked behavioral difference. These are
vertical proofs, not a reusable product foundation. The capability path must
still establish, in a deliberate dependency order:

- interaction among multiple actors, including groups, organisations, and
  non-human systems;
- actor scheduling and interaction mechanics;
- a general sensing or visibility model, rather than explicitly listed visible
  entity IDs;
- subjective state, memory, persistence, and replay where they are needed for
  the product;
- general actions, map topology, and event-log facilities where they are
  needed for the product;

The platform needs the following capabilities in dependency order:

1. A shared authoritative world that hosts heterogeneous participants and
   accepts bounded action proposals through domain-provided resolvers.
2. An execution loop that schedules participants, derives each actor's
   accessible view, obtains validated actor-owned sensemaking, and feeds
   committed outcomes into later turns.
3. An inspectable canonical event history that records the actor's available
   information, proposal, outcome, and presentation boundary independently of
   any one domain.
4. A composition boundary through which a builder can select scenario content,
   actor profiles, action/resolution modules, access policies, and actor
   decision policies without the engine inventing their domain policy.
5. Independent game and simulation applications that can add spatial,
   economic, group, organisational, or non-human mechanics without changing
   the generic engine or one another.

The roadmap should deliver these as coherent construction outcomes, beginning
with the foundation that makes the later modules possible. Existing proofs are
temporary reference material, not compatibility requirements or gates requiring
further experiments.
