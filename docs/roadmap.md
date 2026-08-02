# Roadmap

This document owns ordered incomplete outcomes. Completion evidence belongs in
[experiment evidence](evidence/README.md).

## 1. Build the general simulation-platform foundation

Create the domain-neutral engine foundation for simulations with heterogeneous
actors. A builder can compose a scenario from a shared authoritative world,
participant profiles, and replaceable domain modules; the engine can schedule
actors, derive each actor's permitted view, mediate and validate its
actor-owned questions, receive a bounded proposal, and commit or reject the
canonical outcome. Every completed turn is available as an inspectable
canonical record; presentation remains post-resolution and non-authoritative.

The outcome is platform construction, not an experiment or an application
module. It establishes generic contracts and composition seams without making
spatial, economic, or property-game mechanics part of the engine.

**Decision unlocked:** establish the stable engine seams that later spatial,
economic, group, organisational, and non-human modules can use without
changing generic execution or actor mediation.

**Observable behavior:** a builder can compose a simulation from the generic
engine and supplied modules; the engine coordinates multiple participants in
one canonical world, keeps each actor's permitted view separate, and emits an
inspectable turn record without interpreting domain state or mechanics itself.

**Boundaries for this outcome:** the Technical Lead chooses the smallest
initial module API and migration path. Do not promise a universal YAML DSL,
general map topology, persistence, or every actor type in this
outcome. Those build on the foundation once its generic seams exist. As part of
this milestone, remove the old beast and trader proof code, scenarios,
profiles, and tests; they are superseded scaffolding, not compatibility
fixtures.

## 2. Apply the platform to a two-player property-board game

Build an original, simplified property-board game as the first application of
the platform foundation. Two actors with distinct profiles compete in one
shared game. The game uses a small, fixed board (eight spaces at most),
deterministic movement, a small set of purchasable properties with fixed prices
and rent, and a bounded buy-or-decline proposal on an unowned property. A
landing on an owned property creates a deterministic rent obligation. Cash,
position, ownership, and turn order become canonical feedback for later turns.
The game ends after a fixed turn limit or when a player cannot pay an
obligation.

**Decision unlocked:** determine which domain-module improvements the general
platform needs after a real application, without promoting property-game rules
into the engine by default.

**Observable behavior:** the two actors run on the platform from separately
authored profiles. They receive the same permitted game facts but can have
different plain-language intent and actor-owned binary questions—for example,
acquisition versus preserving cash. The engine validates answers and resolves
only bounded game proposals; neither profile nor language-model output changes
money, ownership, movement, or rent directly. An observer can inspect the
resulting canonical event sequence and actor-specific decision records.

**Boundaries for this outcome:** exclude auctions, cards, jail, buildings,
negotiation, chance-style spaces, trading between players, variable pricing,
and Monopoly-specific names or rules. Do not add mechanics merely to imitate
Monopoly; every included rule must exercise a platform boundary or make the
two actors' competition legible.
