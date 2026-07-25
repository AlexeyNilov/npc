# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Separate LLM semantic interpretation from NPC authority

**Status:** Superseded

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

**Consequences:** This trader-specific decision is retained as historical
rationale. Its primary-intent and expressive-dialogue implementation has been
removed; the current authority boundary is defined by the decision below.

### 2026-07-25: Keep shared LLM perception separate from creature authority

**Status:** Accepted

**Context:** The verified wolf and fox delivery reuses one LLM-backed threat
perception while requiring different deterministic actions. The model can
propose whether a player message contains a threat and cite player text, but it
cannot be allowed to choose whether a creature attacks or flees.

**Decision:** Treat the shared target-aware threat detector as an untrusted
perception capability. It emits only `threat`, `certainty`, and player-text
evidence. Deterministic validation accepts a finite in-range certainty and
grounds a `true` answer in the player message. Each creature-local policy alone
maps accepted perception to action: the wolf attacks, the fox flees, and every
false or rejected result does nothing. Certainty is trace-only.

**Consequences:** The shared detector may be reused without a registry or
generic actor framework. A later abstraction needs new evidence from a
materially different capability or creature policy.

### 2026-07-25: Render completed actor outcomes with a non-authoritative LLM narrator

**Status:** Accepted

**Context:** In the text-based actor reality, the player needs a textual account
of what the fox did. The completed closed rendering experiment preserves the
authority boundary, but its two preapproved sentences and fixture renderer do
not exercise an LLM narrator.

**Decision:** After deterministic perception, choice, action execution, and
feedback are complete, use the configured LLM to narrate the completed action
for the player. The narrator receives only the completed event data required to
describe that action. Its response is presentation data: it cannot choose or
change an action, distance, outcome, or feedback, and it never becomes
canonical world state or input to a later turn. An unavailable or unusable
response has a deterministic fallback.

**Consequences:** The next outcome must demonstrate a real configured-model
invocation rather than only a fixture renderer, while preserving an explicit
trace boundary between the canonical event and narration. The initial narrator
is limited to describing the completed action; whether to allow extra flavour
or assertions beyond that action remains unresolved.

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

### 2026-07-25: Use YAML scenarios for fixed corpora

**Status:** Accepted

**Context:** The fixed creature corpora need checked-in, human-readable,
reproducible inputs. Python's standard library does not parse YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** PyYAML is the only current runtime dependency because the
wolf and fox threat corpora use YAML.
