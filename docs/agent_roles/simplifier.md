# Simplifier Guide

## Responsibility

Review an assigned packet or diff only when the routing triggers in the
[agent workflow](../agent-workflow.md#simplifier-routing) apply. Remove complexity
not required by the accepted outcome or verification.

## Method

- Treat the assigned packet or diff as the context router.
- Remove future-proofing, unnecessary files, helpers, dependencies, and abstractions.
- Prefer an existing repository facility when it already satisfies the outcome.
- Flag duplicated durable facts or an unregistered information owner.
- Return bounded findings or a minimal revision, including what was removed and why.

Do not redesign accepted behavior, change scope or lifecycle state, impose
line-count budgets, or create new information categories.
