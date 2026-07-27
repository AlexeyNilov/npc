# Decisions

This document owns consequential choices and their rationale.

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
