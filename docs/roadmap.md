# Roadmap

This document owns ordered incomplete outcomes. Completion evidence belongs in
[experiment evidence](evidence/README.md).

## 1. Build the modular simulation foundation

Create the reusable engine foundation for simulations with heterogeneous
actors. A builder can compose a scenario from a shared authoritative world,
participant profiles, and domain modules; the engine can schedule actors,
derive each actor's permitted view, mediate and validate its actor-owned
questions, receive a bounded proposal, and commit or reject the canonical
outcome. Every completed turn is available as an inspectable canonical record;
presentation remains post-resolution and non-authoritative.

The outcome is a platform construction step, not an experiment. The current
beast and trader demonstrations are temporary reference material while the
replacement is built. Once the foundation covers their useful boundaries, remove
their proof-specific code, scenarios, profiles, and tests; they are not
templates for the new public schema or compatibility fixtures.

**Decision unlocked:** establish the stable engine seams that later spatial,
economic, group, organisational, and non-human modules can use without
changing generic execution or actor mediation.

**Observable behavior:** a builder can run a composed, shared-world simulation
with more than one participant; a participant's accepted outcome becomes
canonical feedback visible only as allowed to later participants; observer
inspection distinguishes the actor-accessible view, validated sensemaking,
proposal, authoritative outcome, and any non-authoritative narration.

**Boundaries for this outcome:** the Technical Lead chooses the smallest
initial module API and migration path. Do not promise a universal YAML DSL,
general map topology, persistence, replay UI, negotiation, or every actor type
in this outcome. Those build on the foundation once its generic seams exist.
