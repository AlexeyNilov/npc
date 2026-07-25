# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Separate LLM semantic interpretation from NPC authority

**Status:** Accepted

**Context:** Natural-language player input needs an LLM to identify useful
meaning beyond fixed command templates. The same model can invent trader facts,
completed actions, commitments, or history that do not exist. The first trader
also needs genuine small talk rather than wholly templated dialogue.

**Decision:** Treat the LLM as an untrusted semantic sensor. For the first
milestone it proposes one primary player intent and the supporting player-text
evidence. Deterministic code routes that intent:

- An **authoritative** intent can affect an NPC decision only after its fields
  are grounded in the player text and authoritative trader/player context.
- An **expressive** intent may receive free-form, persona-consistent dialogue,
  but cannot assert canonical trader facts, commitments, completed actions, or
  create authoritative state or durable memory.
- An unsupported, unclear, or multi-intent message causes no authoritative
  state change. Multi-intent interpretation is deferred.

Player statements are claims, requests, or proposals; they do not establish
world facts merely because the LLM recognized them.

**Alternatives considered:** Let the LLM select actions or write memory; use
only deterministic command templates; or make all dialogue templated. The
first grants uninspectable authority, while the latter two cannot deliver the
intended natural-language interaction and small-talk freedom.

**Consequences:** The product needs an inspectable grounded-perception contract
and an explicit expressive-dialogue policy. The exact balance of generation and
output controls remains an experiment question; free-form text is not a route
around the authority boundary.

### 2026-07-25: Preserve experiment evidence independently of implementation

**Status:** Accepted

**Context:** The project deliberately removes unsuccessful scaffolding, but
without a durable record its observations are compressed into later decisions
or lost. That encourages re-running the same work and makes roadmap choices
look like implementation preferences rather than evidence-led bets.

**Decision:** Keep one concise experiment-evidence record for every bounded
experiment. The record owns what the experiment demonstrated or refuted;
requirements, architecture, roadmap, and decisions retain their existing,
separate ownership.

**Consequences:** Removing code does not remove its learning. A small
documentation step is required before an experiment starts and when it is
reviewed.

### 2026-07-25: Use YAML scenarios for the initial trader experiment

**Status:** Accepted

**Context:** The first trader-decision experiment needs checked-in,
human-readable, reproducible inputs. Python's standard library does not parse
YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** The scenario is reviewable outside Python and PyYAML is the
only current runtime dependency.
