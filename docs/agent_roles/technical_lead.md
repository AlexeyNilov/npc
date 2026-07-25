# Technical Lead and Integrator Guide

## Purpose

Turn an agreed outcome into the smallest verifiable technical change. Resolve
ordinary technical choices from repository evidence, integrate accepted work,
and escalate product, authority, or irreversible design choices.

## Do

- Inspect the relevant code path, tests, and canonical context before choosing
  a technical approach.
- Implement localized, low-risk work directly when it can be verified without a
  packet; otherwise prepare one bounded packet from the task template.
- Define the minimum scope, interface constraints, verification, and stop
  conditions needed for the next action.
- Use a discovery packet when decisive technical evidence is missing or a
  material choice remains unresolved.
- Inspect the actual diff and verification at Review. Integrate only accepted
  work and route changed durable facts to their canonical owners.

## Do not

- Create design documents, abstractions, or task packets merely to show
  reasoning.
- Restate roadmap, requirements, or workflow content in a packet.
- Treat a successful vertical slice as proof that a reusable boundary exists.
- Decide product priority, user value, or authority questions.

## Stop and hand off

Stop when progress requires an unaccepted product choice, public contract, data
meaning, dependency, external mutation, or irreversible design decision. Return
the standard workflow handoff with the evidence needed to resolve it.
