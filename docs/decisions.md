# Decisions

This document owns consequential choices, alternatives, and rationale.

## Why record decisions

Write down key development decisions while the context is fresh. A short note today can save hours later by explaining what was chosen, what was rejected, and why the trade-off made sense at the time.

## Guidance

Use a lightweight Architecture Decision Record (ADR) style:

* Record decisions that affect architecture, data flow, public APIs, dependencies, deployment, security, or long-term maintenance.
* Write the decision when it is made, not after the context has faded.
* Prefer short entries that explain the context, decision, alternatives, and consequences.
* Include enough reasoning for a future maintainer to understand the trade-off.
* Do not document every small implementation detail; focus on choices that would be costly or confusing to rediscover.
* Update or supersede earlier decisions instead of silently rewriting history.

## Entry template

```markdown
### YYYY-MM-DD: Decision title

**Status:** Proposed | Accepted | Superseded

**Context:** What problem, constraint, or trade-off led to this decision?

**Decision:** What was chosen?

**Alternatives considered:** What other options were rejected, and why?

**Consequences:** What becomes easier, harder, riskier, or more constrained?
```

## Actual decisions

### 2026-07-25: Use YAML scenarios for the initial trader experiment

**Status:** Accepted

**Context:** The first trader-decision experiment needs a checked-in,
human-readable, reproducible definition of its initial state and proposals.
Python's standard library does not parse YAML.

**Decision:** Store the initial experiment scenario in YAML and add PyYAML as
the runtime parser.

**Alternatives considered:** Hard-code the scenario in Python, or add a custom
restricted YAML parser. Hard-coding obscures the explicit experiment inputs;
a custom parser adds needless behavior to own and test.

**Consequences:** The application gains one runtime dependency and its scenario
format becomes a small, reviewable external input boundary.

### 2026-07-25: Keep core actor decisions deterministic

**Status:** Accepted

**Context:** The project needs agent behaviour that can be tested and
reproduced while still supporting natural-language interaction and rich
proposals.

**Decision:** Use LLMs only as supporting tools for information extraction,
narration, and generation of plans or proposals. The core engine remains the
authoritative deterministic decision-maker.

**Alternatives considered:** Letting an LLM make substantive actor decisions.
This is not the preferred direction because it would weaken reproducibility and
testability.

**Consequences:** The internal design must be discovered and validated through
experiments. LLM output cannot by itself determine an actor's authoritative
state changes or final choices.

### 2026-07-25: Use a local-LLM terminal session for the first trader playtest

**Status:** Accepted

**Context:** The first conversational playtest must exercise natural-language
interaction with the configured local LLM, while remaining the smallest
observable experiment. The developer confirmed that a terminal interface and
state lasting only for the current program session are sufficient.

**Decision:** Provide one terminal command backed by the configured local LLM.
Keep one trader/player state and conversation history in memory for the
process. Require the LLM to return a constrained machine-readable candidate
trade alongside its narration; validate that candidate before passing it to the
deterministic decision engine.

**Alternatives considered:** A browser interface, persistence across launches,
or an LLM that directly changes state. They exceed the smallest playtest or
would break the deterministic authority boundary.

**Consequences:** Live play requires the local LLM to be reachable. Automated
tests must replace the LLM boundary with deterministic responses, and malformed
model output becomes a normal no-state-change path.

### 2026-07-25: Gate trade extraction with verbatim player-message evidence

**Status:** Accepted

**Context:** A structured LLM candidate can still invent a sale, item, price,
or direction that the player did not explicitly offer. The terminal playtest
supports exactly one transaction shape, so an LLM interpretation alone cannot
authorize its economic commitment.

**Decision:** Treat the model's candidate as untrusted extraction. Accept it
only when its fixed schema values and exact, ordered evidence excerpts prove an
explicit sale by the player of one `healing herb` to the trader for positive
decimal-digit `gold`; then pass the resulting `Offer` to the deterministic
evaluator.

**Alternatives considered:** Match one fixed player-message template. That
would be simpler to validate but would unnecessarily reject varied filler and
wording around the supported word-level grammar.

**Consequences:** The conversation boundary is deterministic and repeatable
without claiming the model itself is deterministic. Messages that cannot prove
the sole offer shape remain narration-only, and future transaction shapes need
their own explicit contract.
