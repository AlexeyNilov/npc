# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Keep LLM perception separate from fox authority

**Status:** Accepted

**Context:** The verified fox loop uses LLM-backed threat and food-offer
perceptions. The model can propose a player-text fact and cite player text, but
it cannot be allowed to choose whether the fox flees, approaches, or does
nothing.

**Decision:** Treat each fox perception as an untrusted sensor. It emits only
its boolean result, `certainty`, and player-text evidence. Deterministic
validation accepts a finite in-range certainty and grounds a `true` answer in
the player message. The fox-local policy alone maps accepted perceptions to
action; false or rejected results do nothing. Certainty is trace-only.

**Consequences:** The sensors remain narrow functions, not a registry or
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
response has a deterministic fallback. Arbitrary concise narration is allowed
to keep the implementation small and the player experience expressive, rather
than structurally rejecting every claim beyond the completed action.

**Consequences:** The configured-model boundary is verified. Free-form flavour
may still be misleading or false to a player even though it cannot alter
canonical state; this is an accepted residual risk. The action-only input,
instruction to best-effort narrate only the completed action and avoid
unsupported claims, explicit `Narration (non-authoritative)` presentation
label, response-length limit, deterministic fallback, and retained trace
mitigate it without enforcing factual accuracy. If player trust remains a
demonstrated problem, revisit claim validation or a more constrained
presentation.

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

**Consequences:** PyYAML is the only current runtime dependency because the fox
feedback and outcome-rendering corpora use YAML.
