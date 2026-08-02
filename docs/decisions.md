# Decisions

This document owns consequential choices and their rationale only when they
are enduring, project-level commitments: they constrain multiple outcomes,
the target product model, or a future choice beyond the outcome that prompted
them.

Do not record a choice here merely because it was accepted. A choice,
assumption, or boundary deliberately limited to one open roadmap outcome
belongs under that outcome in [the roadmap](roadmap.md), together with its
rationale and expiry or non-generality boundary. Observed experimental results
belong in [experiment evidence](evidence/README.md), and required observable
behavior belongs in [requirements](requirements.md).

Before adding an entry, ask: “If this outcome were completed and later removed
from the roadmap, would this choice still constrain a future product outcome?”
If not, keep it with the outcome. Promote it here only when later evidence or
an accepted change makes it a durable project commitment.

### 2026-07-26: Use Natural Language as the Default Interface Between Actors and the World

**Status:** Accepted

**Context:**

Actors need to understand the simulation without hardcoding world-specific code into every actor. Tying actors directly to simulation code ruins portability, but making a separate AI request for every question an actor asks gets too expensive.

**Decision:**

Use plain human language as the primary communication bridge between world data and actor cognition.

1. **The Simulation** filters world data down to only what the actor can actually perceive.
2. **The Actor** provides its profile (senses, knowledge, biases, context, and current questions).
3. **An LLM** combines these into a single subjective view (percept) and answers all the actor's questions in **a single request** to save costs.

* An actor's perception can be wrong or distorted, but that confusion stays local and never alters official world data.
* Actors only return a strict **action proposal**. Only the central simulation engine can actually execute actions and update official reality.

**Consequences:**

* **Independent Development:** World engines and actor behaviors can be built separately without sharing code structures.
* **Strict Contracts Remain:** Natural language makes communication flexible, but defined action proposal rules are still strictly required.

### 2026-08-02: Keep the simulation platform separate from applications

**Status:** Accepted

**Context:**

The first planned application is a simplified two-player property-board game,
but the product vision is a shared platform for many games and simulations.
Embedding property-game concepts in the engine would make that first
application a hidden constraint on every later simulation.

**Decision:**

The simulation platform owns generic composition, execution, actor mediation,
authoritative transition coordination, and inspection. Each game or simulation
is an independent application that supplies its own world model, domain state,
rules, action/resolution modules, access policy, and actor profiles through the
platform's composition boundary. The property-board game must depend on the
platform; the platform must not depend on it.

**Consequences:**

* Domain concepts such as boards, cash, properties, rent, and turns are owned
  by the property-game application, not the generic platform.
* A later builder can compose a different game or simulation without carrying
  the property-game module or modifying platform internals.
* Changes to a domain application may identify a missing generic capability,
  but that capability enters the platform only when it is truly domain-neutral.
