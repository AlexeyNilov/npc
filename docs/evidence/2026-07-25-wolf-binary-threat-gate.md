# Experiment: wolf binary threat-perception gate

**Status:** Complete

**Date:** 2026-07-25

**Roadmap outcome:** Completed; see the [current roadmap](../roadmap.md).

## Decision unlocked

Whether future creature perceptions should be independent, action-relevant binary
questions, and whether recorded model certainty merits a later calibration test
without granting it authority.

## Hypothesis

For one player message, one LLM question can propose a binary answer to whether
the player makes a credible hostile threat toward the wolf. Deterministic code
can permit `attack` only for a grounded `true` answer, while `false`, malformed,
out-of-range-certainty, and ungrounded candidates all produce `do_nothing`.

Assumptions: the completion adapter remains available for an optional live corpus
run; fixture completions are sufficient to verify parsing, validation, and
policy; and "credible hostile threat toward the wolf" needs no world facts beyond
the player-message text. Model certainty is observational data only, so this
experiment does not test its calibration or use it as an action threshold.

## Observable behavior

A developer can run a checked-in corpus of independent player messages and
inspect the expected binary threat/action pair, raw candidate, parsed binary
candidate, certainty, evidence, validation result, and deterministic action.

- **Goal:** defend the wolf's territorial boundary.
- **Perception:** an untrusted binary threat candidate, reported certainty, and
  evidence when the candidate is `true`.
- **Intent or choice:** deterministic acceptance or rejection of the proposed
  perception.
- **Action:** `attack` only after an accepted grounded `true`; otherwise
  `do_nothing`.
- **Outcome:** one machine-readable trace per independent corpus case.
- **Feedback or retained history:** none.
- **Later decision affected:** whether a later creature experiment should keep
  perception questions independent and whether certainty is useful for a
  separate calibration experiment.

## Design

- **Authoritative inputs and initial state:** one player-message string; the
  model response is untrusted input; the wolf has no mutable state.
- **Scenario timeline or action contracts:** the sensor makes exactly one
  request and returns JSON with exactly `threat`, `certainty`, and `evidence`.
  `threat` is a JSON boolean; `certainty` is a finite JSON number in `[0, 1]`;
  `evidence` is a non-empty verbatim player-message substring for `true` and
  `null` for `false`. Deterministic validation rejects any other shape, an
  out-of-range or non-finite certainty, a `true` candidate with empty evidence,
  or `true` evidence absent from the player message. Certainty has no policy
  branch or threshold.
- **Expected trace or outputs:** JSON contains the corpus case identifier,
  player message, expected threat and action, raw candidate, parsed candidate
  or null, validation result, and action. The parsed candidate exposes its
  certainty and evidence.
- **Deliberate exclusions:** trader facts or state, transactions, world
  simulation, reply generation, multi-intent interpretation, creature memory,
  certainty-based authority, and actions other than `attack` and `do_nothing`.
- **Candidate durable elements and disposable scaffolding:** the
  candidate-validation-policy seam is experiment-local scaffolding. No reusable
  perception framework is claimed; a materially different second creature
  scenario is required before promotion.

## Signals and stop rule

- **Support signal:** each accepted `true` has exact player-text evidence and
  produces `attack`; every `false`, malformed, out-of-range-certainty, or
  ungrounded candidate produces `do_nothing`; the corpus displays expected
  threat/action pairs; and changing only certainty does not change action.
- **Rejection signal:** an attack can result without valid player-text evidence,
  the contract needs invented world facts, or explaining the action needs more
  than one LLM question.
- **Inconclusive condition:** deterministic fixture verification passes but a
  live corpus run does not provide enough valid traces to assess the sensor on
  its fixed corpus.
- **Stop rule:** after the corpus, malformed and ungrounded `true` fixtures,
  out-of-range-certainty fixtures, and deterministic policy tests are run,
  complete this record. Do not add state, dialogue, world machinery, memory,
  labels, certainty authority, or additional actions to compensate.

## Result

- **Observed result:** The checked-in fixtures support the binary authority
  boundary: a grounded `true` candidate yields `attack`; an accepted `false`,
  malformed candidate, empty or ungrounded `true` evidence, and an out-of-range
  non-finite, or arbitrarily large integer certainty all yield `do_nothing`.
  The four-case corpus contains direct-threat, calm/friendly, fearful, and
  ambiguous messages and displays an expected threat/action pair for each case.
  Changing only valid `true` certainty from `0.01` to `0.99` leaves the action
  as `attack`.
- **Reproducibility evidence:** Behavioral tests were written before the module
  existed and initially failed during collection with `ModuleNotFoundError: No
  module named 'npc.experiments.wolf_threat'`. After implementation,
  `.venv/bin/pytest tests/test_wolf_threat.py` passed (9 tests) and
  `.venv/bin/pytest tests/test_wolf_affect.py` passed (8 tests). `make check`
  passed: ruff formatting and lint, mypy, and all 38 tests. `git diff --check`
  passed. The project interpreter ran the fixed corpus and captured four valid
  JSON traces: the direct threat was accepted as `true` and attacked; the calm,
  fearful, and ambiguous messages were accepted as `false` and did nothing.
- **Interpretation and limits:** The fixed corpus supports the binary question
  for this narrow threat boundary: model output cannot select an attack without
  an accepted `true` and exact player-text evidence, while certainty remains
  observational data. One corpus run does not establish general model accuracy
  or certainty calibration.
- **Decision or unresolved question created:** Decide whether observed product
  behavior warrants a second independent, action-relevant binary perception
  question or a separate certainty-calibration experiment. Do not select one
  without a documented limitation or decision it must address.
