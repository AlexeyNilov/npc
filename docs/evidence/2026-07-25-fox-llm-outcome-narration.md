# Experiment: configured non-authoritative fox outcome narration

**Status:** Inconclusive

**Date:** 2026-07-25

**Roadmap outcome:** [Invoke an LLM as a non-authoritative fox outcome narrator](../roadmap.md#1-invoke-an-llm-as-a-non-authoritative-fox-outcome-narrator)

## Decision unlocked

Whether a configured LLM narration boundary is useful enough to retain, and
whether later work needs factual constraints beyond the completed action.

## Hypothesis

A configured LLM can narrate one completed fox action in arbitrary concise
text without changing the canonical action or feedback.

Assumptions: the configured endpoint is available and its response can be
nonblank and no longer than 280 Unicode characters. The claim is limited to
non-authoritative presentation, not factual accuracy.

## Observable behavior

A developer can run `python -m npc.experiments.fox_outcome_rendering
--configured-narrator` and inspect one JSON-safe trace per fixture canonical
turn. Each trace retains the completed action, deterministic outcome and
feedback, action-only narration prompt, raw response or failure, validation,
rendered text or fallback, and `non_authoritative: true`.

## Design

- **Authoritative inputs and initial state:** Fixture player message, starting
  distance, and deterministic completed turn.
- **Scenario timeline or action contracts:** Complete the fox turn first; then
  make exactly one configured narrator call from only `executed_action`.
- **Expected trace or outputs:** Free-form narration is accepted when nonblank
  and at most 280 Unicode characters; blank, oversized, and exceptional
  narrator responses use the deterministic fallback.
- **Deliberate exclusions:** Narration is not evidence, choice, world state,
  feedback, history, player-input interpretation, or semantic fact checking.
- **Candidate durable elements and disposable scaffolding:** The action-only
  boundary and immutable trace are candidates; YAML fixture narrators are
  disposable experiment scaffolding.

## Signals and stop rule

- **Support signal:** Configured traces for `flee` and `do_nothing` have one
  accepted call each and unchanged canonical turns.
- **Rejection signal:** The call changes canonical data or needs data beyond
  the completed action.
- **Inconclusive condition:** The configured endpoint is unavailable, or its
  observed response is blank or oversized.
- **Stop rule:** Record fixture results and configured runs for `flee`,
  `do_nothing`, and an unavailable or unusable response; then stop.

## Result

Complete at Review.

- **Observed result:** Fixture coverage accepts free-form `flee` and
  `do_nothing` narration and exercises blank, oversized, and exceptional
  fallback paths. The configured command was invoked on 2026-07-25 and exited
  successfully, but this execution environment returned no inspectable trace
  output; it therefore did not provide the required configured-model evidence.
- **Reproducibility evidence:** `.venv/bin/python -m pytest
  tests/test_fox_outcome_rendering.py`; fixture command:
  `.venv/bin/python -m npc.experiments.fox_outcome_rendering`.
- **Interpretation and limits:** Fixture evidence establishes the boundary and
  fallback behavior only. The missing configured trace means this experiment
  does not demonstrate a configured-model response or its usability.
- **Decision or unresolved question created:** Whether actual free-form model
  narration is useful, and whether it needs factual constraints.
- **Canonical follow-up:** [Roadmap outcome](../roadmap.md#1-invoke-an-llm-as-a-non-authoritative-fox-outcome-narrator).
