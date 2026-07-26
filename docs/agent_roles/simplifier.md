# Simplifier Guide

## Responsibility

Review an assigned packet or diff only when the
[workflow triggers](../agent-workflow.md#enter-the-implementation-loop) apply.
Remove complexity not required by the accepted outcome or verification.

## Method

- Treat the assigned packet or diff as the context router.
- Remove future-proofing, unnecessary files, helpers, dependencies, and
  abstractions; prefer an existing repository facility when it fits.
- When the packet changes domain information, flag any added label, predicate,
  state, event, transition, or threshold that lacks the packet's required
  source, accepted transformation, authority, or lifecycle. Do not invent a
  missing meaning to make the change fit.
- Return bounded findings or a minimal revision, including what was removed and
  why.

Do not redesign accepted behavior, change scope or lifecycle state, impose
line-count budgets, or create new information categories.
