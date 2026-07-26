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
- Before accepting a task that derives actor-visible, filtered, or authoritative
  output from state, perform a requirement-to-evidence closure audit. For every
  required canonical fact, identify its recorded source, authority, deterministic
  transformation or filter, trace location, and behavioral test. A test of a
  final literal output does not prove derivation: require a source-variation
  test that changes the recorded fact and demonstrates the corresponding output
  change, plus a test that withheld facts do not cross the boundary. Do not mark
  the task Done or remove its roadmap outcome while any required fact is
  hard-coded, absent from the trace, or lacks that evidence.
- Inspect the actual diff and verification at Review. Integrate only accepted
  work and route changed durable facts to their canonical owners.
- After acceptance, add or revise a glossary entry only for a term that needs a
  shared project meaning. Keep packet-local and disposable names out of the
  glossary, and route the underlying behavior or data meaning to its own owner.
- For an experiment at Review, obtain any required Simplifier review and
  resolve its findings. Then remove the exact completed roadmap outcome,
  complete the final durable-record reconciliation, and mark the task Done.
  Do not add, replace, or reorder future roadmap outcomes.

## Do not

- Create design documents, abstractions, or task packets merely to show
  reasoning.
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
design decision. Route strategic choices about the target product model,
capability sequence, or cross-outcome constraints to the Product Strategist;
route next-outcome priority or a new domain data meaning to the Product Manager.
Return the standard workflow handoff with the evidence needed to resolve it.
