# Experiment: village emergency-food rationing portability

**Status:** Planned

**Date:** 2026-07-26

**Roadmap outcome:** [Test cross-scale portability of the semantic and causal
contracts](../roadmap.md#1-test-cross-scale-portability-of-the-semantic-and-causal-contracts)

## Decision unlocked

Whether to retain natural language as the default actor-world semantic
interface for the next capability expansion, or reconsider a structured
supplement/replacement or narrower product scope.

## Hypothesis

The established actor-accessible-substate, epistemic-profile,
subjective-percept, actor-owned-question, bounded-proposal, and
authoritative-resolution contracts support a village relief allocation without
shared schema-specific sensemaking code, while preserving inspectable,
replayable authoritative causality.

## Observable behavior

Two household claimants receive separate private views and submit bounded
four-unit claims. A relief-organisation actor receives only the public claim
ledger and reserve, forms a percept, and proposes an allocation. The simulation
core validates and commits the allocation, produces actor-specific feedback,
and records a replayable trace. At six reserve units the allocation is 4/2; a
reserve-only change to four units produces 4/0 without revealing private
household information.

## Design

- **Authoritative inputs and initial state:** six-unit reserve, no committed
  allocations, and two fixed potential four-unit claims ranked priority tiers
  one then two. Valid household submissions form the public claim ledger.
- **Scenario timeline or action contracts:** household claim mediation;
  organisation allocation mediation; core validation and commit; feedback and
  trace recording. The organisation may propose but never commit allocation.
- **Expected trace or outputs:** separate actor-local records, submitted
  claims, allocation proposal, validation decision, transitions, resulting
  reserve and allocations, and actor-specific feedback. The corpus includes
  the six-unit case, four-unit reserve variation, and invalid allocation case.
- **Deliberate exclusions:** village management, eligibility or fairness
  models beyond the fixed priority rule, persistent household state, and a
  shared actor/world framework.
- **Candidate durable elements and disposable scaffolding:** all module, trace
  types, corpus, and resolver code are disposable bounded-scenario scaffolding;
  verified observable behavior belongs in Requirements.

## Signals and stop rule

- **Support signal:** the slice enforces separate household and organisation
  inputs, accepts only bounded proposals, performs deterministic authoritative
  allocation, and replays both reserve cases without mediation or leakage.
- **Rejection signal:** natural-language mediation repeatedly loses
  action-relevant precision, cannot meet usable cost or latency, or requires
  shared schema-specific sensemaking logic.
- **Inconclusive condition:** fixture-only behavior passes but does not expose
  the claimed information boundary or source-state variation.
- **Stop rule:** evaluate this one contrasting slice and the established
  fox-and-hunter slice only; stop when the evidence distinguishes the decision
  options and do not introduce a general framework or further domain.

## Result

At task Review, complete every field and set the evidence status to `Review`.
The Technical Lead sets the final status after required review and roadmap
closure.

- **Observed result:** Pending.
- **Reproducibility evidence:** Pending.
- **Interpretation and limits:** Pending.
- **Decision or unresolved question created:** Pending.
- **Canonical follow-up:** Pending.
