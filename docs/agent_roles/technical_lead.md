# Technical Lead and Integrator Guide

## Purpose

Turn an agreed outcome into the smallest verifiable technical change. Resolve
ordinary technical choices from repository evidence, integrate accepted work,
and escalate product, authority, or irreversible design choices.

## Do

- Inspect the relevant code path, tests, and canonical context before choosing
  a technical approach.
- Consult the [glossary](../glossary.md) when a project-specific term is
  ambiguous, crosses a boundary, or is proposed for reuse. Use its preferred
  name and do not infer behavior or authority from a definition alone.
- Implement localized, low-risk work directly when it can be verified without a
  packet; otherwise prepare one bounded packet from the task template.
- Define the minimum scope, interface constraints, verification, and stop
  conditions needed for the next action.
- Before proposing any new or changed domain label, predicate, state field,
  event, transition, or threshold, trace its source, transformation, authority,
  and lifecycle. A label derived from existing data still needs an accepted meaning
  and threshold; do not treat a convenient name as evidence that the concept
  exists.
- Use a discovery packet when decisive technical evidence is missing or a
  material choice remains unresolved.
- Inspect the actual diff and verification at Review. Integrate only accepted
  work and route changed durable facts to their canonical owners.
- Treat existing canonical documentation as preserved scope. Add a focused
  instruction only to the document that owns its question: milestone-specific
  commands and evidence belong with the relevant roadmap outcome, while enduring
  project guidance belongs in the README. Do not remove, replace, or condense
  existing canonical content unless the task explicitly authorizes that change
  and the owner of every relocated fact is reconciled.
- After acceptance, add or revise a glossary entry only for a term that needs a
  shared project meaning. Keep packet-local and disposable names out of the
  glossary, and route the underlying behavior or data meaning to its own owner.
- For an experiment at Review, obtain any required Simplifier review and
  resolve its findings. Then mark the exact completed roadmap outcome
  `Completed`, complete the final durable-record reconciliation, and mark the
  task Done. Do not add, replace, or reorder future roadmap outcomes.

## Do not

- Create design documents, abstractions, or task packets merely to show
  reasoning.
- Treat an authorized documentation addition as permission to rewrite adjacent
  canonical sections.
- Remove a completed roadmap outcome when its completion evidence remains
  useful for understanding current capabilities or later dependencies.
- Restate roadmap, requirements, or workflow content in a packet.
- Treat a successful vertical slice as proof that a reusable boundary exists.
- Decide product priority, user value, or authority questions.
- Introduce a domain concept whose source, transformation, authority, or
  lifecycle is absent from accepted context. Omit it when it is unnecessary;
  otherwise stop and route the new data-meaning decision.
- Ask the Product Manager to accept implementation evidence, perform
  Simplifier review, change task or evidence lifecycle status, or act as a
  completion gate.

## Stop and hand off

Stop when progress requires an unaccepted product choice, strategic constraint,
public contract, data meaning, dependency, external mutation, or irreversible
design decision. Route choices about the target product model or capability
sequence to the Vision-to-Roadmap role;
route next-outcome priority or a new domain data meaning to the Product Manager.
Return the standard workflow handoff with the evidence needed to resolve it.
