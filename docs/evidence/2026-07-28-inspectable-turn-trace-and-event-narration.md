# Experiment: Inspectable beast turn trace and resilient event narration

**Status:** Complete

**Date:** 2026-07-28

**Roadmap outcome:** Completed; see the current roadmap.

## Decision unlocked

Determine whether observer-facing inspection and entertaining presentation can
be added to the mediated-perception proof while preserving the separation of
subjective choice, authoritative outcome, and presentation-only narration.

## Hypothesis

For each resolved beast turn, the CLI can display validated actor perception,
the selected bounded attempted proposal, and the resolver's outcome as a
labelled trace, then obtain non-authoritative narration solely from completed
presentation facts without allowing narration to alter canonical state or a
later turn.

Assumptions: deterministic test doubles can supply alternate perception
answers and narration text or failure; the existing perception scenario's
accepted move and rejected `wait` proposal are sufficient proof fixtures.

## Observable behavior

A developer can run focused tests that inspect the trace from both an accepted
and a rejected perception-informed turn. The trace names the validated
perception answers, selected choice and bounded proposal, and authoritative
outcome without requiring narration to establish any fact. A completed outcome
is committed and visible even when the post-resolution narration request is
unavailable or blank; narration does not affect later perception, choice,
proposal, outcome, feedback, or retained history.

## Design

- **Authoritative inputs and initial state:** existing one-beast perception
  scenario, profile, `State`, selected `Proposal`, and resolver `Outcome`.
- **Scenario timeline or action contracts:** validate perception; select and
  construct a proposal; resolve and commit it; render the labelled trace; then
  request and print narration from a completed presentation payload, or print
  an unavailable marker.
- **Expected trace or outputs:** separate labelled perception, choice, and
  authoritative-outcome sections, followed by separate non-authoritative
  narration or an unavailable marker, for accepted and rejected turns.
- **Deliberate exclusions:** narration truthfulness guarantees, raw model
  output display, retries, fallback prose, persistence, replay, streaming,
  general event logs, multi-actor behavior, and later-turn narration feedback.
- **Candidate durable elements and disposable scaffolding:** the post-
  resolution presentation boundary and observer distinction may be documented
  after verification; exact output punctuation, prompt wording, and formatter
  representation remain proof scaffolding.

## Signals and stop rule

- **Support signal:** focused tests prove the trace distinction, causal
  alternate-answer contrast, post-resolution input boundary, and narration
  failure resilience; repository checks pass.
- **Rejection signal:** narration needs hidden data or rule/resolver control,
  can mutate or affect subsequent simulation inputs, or failure hides or
  reverses a resolved outcome.
- **Inconclusive condition:** deterministic doubles cannot establish the
  request ordering, payload boundary, and state behavior without a live
  external service.
- **Stop rule:** stop on any rejection or inconclusive condition; record the
  observed evidence and route a new product or data-meaning choice rather than
  expanding the proof.

## Result

At task Review, complete every field and set the evidence status to `Review`.
The Technical Lead sets the final status after required review and roadmap
closure.

- **Observed result:** Supported. Each resolved perception-fixture turn emits
  deterministic `perception`, `choice`, and `authoritative outcome` sections,
  followed by separately labelled non-authoritative narration. The accepted
  `flee` move and rejected `wait` proposal retain their distinct authoritative
  results. Narration exceptions, non-string responses, and blank responses
  produce the fixed unavailable marker without undoing the resolved state.
- **Reproducibility evidence:** `.venv/bin/python -m pytest -q
  tests/test_yaml_beast_proof.py` passed (24 tests); `make check` passed
  formatting, lint, type checking, and the full test suite (24 tests).
- **Interpretation and limits:** Deterministic doubles establish that narration
  is requested only after resolution, receives only a completed presentation
  payload, and is not retained or used by the next turn. This remains a
  one-beast, presentation-only proof: it does not establish truthful prose,
  persistence, replay, retries, or a general event-log/narration platform.
- **Decision or unresolved question created:** None. The requested boundary is
  demonstrable without adding a domain fact, authority, or lifecycle.
- **Canonical follow-up:** Requirements and Architecture now record the
  verified observer and post-resolution presentation behavior; roadmap outcome
  3 is completed.
