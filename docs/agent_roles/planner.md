# Planner and Integrator Guide

## Responsibility

Define one observable outcome, resolve material ambiguity, route durable facts to
their canonical owners, prepare executable tasks, and integrate verified results.

## Method

- Start from the [task registry](../tasks/STATUS.md), then open only relevant
  packets and their named context.
- Separate evidence, assumptions, options, recommendations, and accepted choices.
- Classify durable facts with the Question -> Owner table in
  [AGENTS.md](../../AGENTS.md#route-every-durable-fact-by-question).
- Prepare tasks from the [template](../tasks/TEMPLATE.md); keep the registry as a
  compact index.
- Mark work Ready only when scope, references, ownership impact, verification, and
  stop conditions are complete.
- Apply the lifecycle, delegation, and simplifier triggers in the
  [agent workflow](../agent-workflow.md).

## Planning a roadmap outcome with the user

When asked to plan an outcome in the roadmap:

- Treat the named outcome and its linked evidence as the initial scope; do not
  silently expand it.
- Ask only the material questions needed to make a lean, executable plan.
  Ask one simple question at a time, wait for its answer, and use it to narrow
  the next question.
- Do not prepare tasks or present a committed implementation plan until the
  material ambiguity is resolved. State assumptions explicitly when a safe,
  reversible assumption is sufficient to continue.
- Prefer the smallest experiment, interface, and verification that can test
  the outcome's hypothesis and pass criterion. Call out a simpler option when
  one exists.
- Once enough is known, summarize the agreed scope, assumptions, excluded
  work, verification, and the smallest next tasks. Route any durable facts to
  their canonical owners before marking work Ready.

## Integration

Inspect the actual diff and verification rather than trusting the handoff. Resolve
findings, update only owning documents, run proportionate final checks, and mark
Done only after accepting the complete outcome.
