# Experiment: village emergency-food rationing portability

**Status:** Complete

**Date:** 2026-07-26

**Roadmap outcome:** Completed; see the current roadmap.

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

- **Observed result:** Supported. The checked-in corpus records accepted 4/2
  and 4/0 priority allocations for six- and four-unit canonical reserves,
  respectively, and rejects the over-reserve 4/4 proposal with unchanged
  canonical state. One behavioral test reuses the same three mediation
  callbacks across the two reserve inputs, derives the organisation response
  from its received reserve observation, and confirms unchanged household
  observations and claims. Behavioral tests also exercise separate actor
  inputs, private-fact exclusion from other requests and feedback, malformed
  and unsupported mediation failure for every actor, JSON-safe traces, and
  replay without a mediation call.
- **Reproducibility evidence:** `.venv/bin/pytest
  tests/test_village_rationing.py` passed (16 tests); focused Ruff and mypy
  checks passed; `make test` and `make check` passed the 72-test repository
  suite; and `git diff --check` passed.
- **Interpretation and limits:** The result supports this fixed, disposable
  three-actor scenario's causal boundary. It does not establish a village
  management model, eligibility or fairness policy beyond the accepted priority
  rule, persistent household state, live-model cost or latency, or a reusable
  framework.
- **Decision or unresolved question created:** The evidence supports retaining
  natural language as the default semantic interface through this contrasting
  allocation slice.
- **Canonical follow-up:** None — completion reconciliation finished.
