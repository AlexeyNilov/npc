# Experiment: non-authoritative rendering of a completed fox outcome

**Status:** Complete

**Date:** 2026-07-25

**Roadmap outcome:** Completed; see the [current roadmap](../roadmap.md).

## Decision unlocked

Whether a renderer limited to a completed authoritative fox action can provide
a useful player-facing message without becoming a source of world facts,
actions, or feedback.

## Hypothesis

After a completed fox turn, an LLM can return a checked player-facing sentence
for only that action while the canonical turn trace and feedback remain
unchanged. Invalid or unavailable rendering can use the deterministic fallback
`The fox's response cannot be rendered.` without changing the completed event.

Assumptions: strict factual rendering is required; the allowed rendered
sentences are `The fox flees.` for completed `flee` and `The fox does nothing.`
for completed `do_nothing`; and any other renderer output is rejected. The
renderer receives only the completed action needed to select that sentence.

## Observable behavior

A developer can run fixed completed-fox-outcome fixtures and inspect the
canonical turn trace, rendering prompt, raw renderer output, rendering
validation result, and player-facing rendering or deterministic fallback.

- **Goal:** present one completed fox outcome without granting presentation
  authority over it.
- **Perception:** none; rendering occurs only after the canonical turn ends.
- **Intent or choice:** the prior deterministic fox choice is retained, not
  reconsidered.
- **Action:** the prior executed `flee` or `do_nothing` is retained, not
  selected by the renderer.
- **Outcome:** a checked rendering or fallback is stored as non-authoritative
  presentation data.
- **Feedback or retained history:** the prior feedback distance remains
  unchanged and renderer output never becomes next-turn input.
- **Later decision affected:** whether this closed, non-authoritative
  presentation boundary is useful before permitting expressive flavour.

## Design

- **Authoritative inputs and initial state:** a completed `TurnTrace` from the
  fox distance-feedback experiment. Renderer output is untrusted.
- **Scenario timeline or action contracts:** finalize the turn and its distance
  before the renderer call; prompt with only its executed action; accept only a
  JSON object whose action matches the completed action and whose message is
  the one allowed exact sentence for that action; otherwise use fallback.
- **Expected trace or outputs:** canonical turn trace, rendering prompt, raw
  output, validation status, rendered message, and a non-authoritative marker.
- **Deliberate exclusions:** dialogue history, player-intent extraction,
  generated state changes, added world facts, multi-turn conversation, flavour
  text, and renderer output as perception or feedback.
- **Candidate durable elements and disposable scaffolding:** the completed-event
  to checked-presentation sequence is under test; the module, fixtures, and
  closed text vocabulary are disposable experiment scaffolding.

## Signals and stop rule

- **Support signal:** valid flee and do-nothing fixtures render only their
  matching exact sentences; malformed, action-mismatched, or failed rendering
  uses fallback while the canonical trace is byte-for-byte equivalent.
- **Rejection signal:** a useful trace requires the renderer to interpret raw
  player text, infer a fact, choose an action, or modify distance or feedback.
- **Inconclusive condition:** the trace cannot show that canonical state was
  finalized before rendering, or cannot distinguish fallback from a completed
  action.
- **Stop rule:** record accepted, malformed, unavailable, and non-action
  fixture behavior, then stop. Do not add dialogue, flavour, history, state,
  or a general presentation framework.

## Result

- **Observed result:** Valid fixture rendering accepts `flee` only as `The fox
  flees.` and `do_nothing` only as `The fox does nothing.` The accepted
  in-range threat preserves its completed `flee` trace and distance `15`; the
  in-range and initially out-of-range non-actions preserve `do_nothing` and
  distances `10` and `11`. Malformed, extra-field, action-mismatched,
  message-mismatched, and failed renderer outputs return the fixed fallback
  without changing any canonical-turn field. The rendering test records one
  renderer call for each requested completed turn; no perception sensor is
  called by rendering.
- **Reproducibility evidence:** Behavioral tests were added before the module
  and initially failed during collection with `ModuleNotFoundError: No module
  named 'npc.experiments.fox_outcome_rendering'`. After implementation,
  `.venv/bin/pytest tests/test_fox_outcome_rendering.py` passed with 5 tests.
  The checked-in fixture traces cover accepted in-range `flee`, in-range and
  initially out-of-range `do_nothing`, malformed output, and renderer failure.
  The packet's existing fox distance and threat modules, `make check`, and
  `git diff --check` are recorded in the implementation handoff.
- **Interpretation and limits:** The trace demonstrates only a closed,
  non-authoritative rendering boundary after a completed fox turn. It does not
  demonstrate reusable presentation, dialogue, flavour generation, world
  facts, state changes, or an event framework.
- **Decision or unresolved question created:** Whether this narrowly checked
  presentation is useful enough to expose to players before adding expressive
  flavour remains unresolved.
- **Canonical follow-up:** The accepted observable behavior and verified
  mechanism are recorded in [requirements](../requirements.md) and
  [architecture](../architecture.md), respectively.
