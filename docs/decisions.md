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

### 2026-07-25: Keep core actor decisions deterministic

**Status:** Proposed

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
