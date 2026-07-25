# Delivery: shared target-aware threat detection

**Status:** Complete

**Date:** 2026-07-25

**Roadmap outcome:** [Reuse threat detection for a fleeing fox](../roadmap.md#reuse-threat-detection-for-a-fleeing-fox)

## Decision unlocked

Whether the verified binary threat contract is a sufficiently small reusable
perception capability for two creatures with different deterministic actions,
without creating a general creature or skill framework.

## Delivery contract

One target-aware threat-detection capability can make exactly one untrusted
binary perception request for either a wolf or a fox, return the same candidate
shape and validation result, and leave the creature-specific policy to map an
accepted `true` to `attack` or `flee` respectively. `false`, malformed,
invalid-certainty, and ungrounded candidates can safely yield `do_nothing` for
both creatures.

Assumptions: a creature's fixed display name is sufficient target context for
this bounded prompt; the existing wolf corpus remains valid; and fixture
completions establish the shared contract and policies independently of a live
model run. Certainty remains recorded observational data, not an authority
threshold. This delivery does not establish a general creature interface or
cross-scenario model accuracy.

## Observable behavior

A developer can run fixed wolf and fox corpora and inspect, per message, the
target-aware raw candidate, parsed candidate, certainty, exact evidence,
validation result, expected threat/action pair, and each creature's
deterministic action.

- **Goal:** detect a credible hostile threat toward the named creature without
  granting the model action authority.
- **Perception:** one untrusted `threat`/`certainty`/`evidence` candidate from
  the shared target-aware capability.
- **Intent or choice:** shared deterministic validation, followed by a
  creature-local deterministic policy.
- **Action:** accepted `true` yields wolf `attack` or fox `flee`; every other
  result yields that creature's `do_nothing`.
- **Outcome:** JSON traces for both independent corpora and paired policy
  fixtures for the same perception.
- **Feedback or retained history:** none.
- **Later decision affected:** whether a materially different perception need
  justifies another independently reusable sensor, not a general registry.

## Design

- **Authoritative inputs and initial state:** player-message string and a
  program-controlled target name; each creature has no mutable state. Model
  output is untrusted input.
- **Scenario timeline or action contracts:** one shared function builds the
  target-aware prompt and performs one completion call. It parses exactly
  `threat`, `certainty`, and `evidence`, retaining the current contract:
  boolean threat, finite non-boolean numeric certainty in `[0, 1]`, non-empty
  verbatim evidence for `true`, and `null` evidence for `false`. Validation
  remains target-independent. Separate wolf and fox policies consume only the
  accepted boolean perception; neither receives certainty or raw model output.
- **Expected trace or outputs:** each trace contains target, case id, player
  message, expected threat/action, raw candidate, parsed candidate or null,
  validation result, and action. The parsed candidate contains certainty and
  evidence.
- **Deliberate exclusions:** creature-specific candidate fields or validators,
  LLM-selected actions, memory, dialogue, world simulation, certainty-based
  authority, and a creature/skill registry or generic actor framework.
- **Candidate durable elements and disposable scaffolding:** the shared
  target-aware detection module is a candidate durable capability; the wolf and
  fox CLI/corpus wrappers remain delivery scaffolding. A third materially
  different creature perception or policy is required before introducing a
  registry or broader abstraction.

## Acceptance and boundary

- **Acceptance evidence:** wolf and fox traces expose the same candidate and
  validation contract; an identical accepted grounded perception yields
  `attack` for wolf and `flee` for fox; every invalid or ungrounded candidate
  yields `do_nothing`; and changing only certainty changes neither policy.
- **Boundary breach:** target-awareness requires creature-specific model fields
  or validation, invalid evidence can cause either action, the policy needs
  more than one model question, or reuse requires a general framework.
- **Completion boundary:** after both corpora, malformed and ungrounded true fixtures,
  and both deterministic policy tests, complete this record. Do not add memory,
  dialogue, world machinery, certainty authority, or a general registry.

## Result

- **Observed result:** The shared detector preserves the exact three-field
  candidate contract and deterministic validation for both targets. The same
  grounded `true` fixture maps to wolf `attack` and fox `flee`; accepted
  `false`, malformed output, ungrounded `true` evidence, non-finite or
  out-of-range certainty, and arbitrarily large integer certainty all map to
  `do_nothing` under the applicable policy. Both four-case corpora include a
  direct threat, calm/friendly, fearful, and ambiguous message. The fox direct
  threat names the fox in the player text. Changing only valid `true` certainty
  from `0.01` to `0.99` changes neither creature's action.
- **Reproducibility evidence:** The new shared/fox behavior tests were added
  before the extraction and initially failed during collection with
  `ModuleNotFoundError: No module named 'npc.experiments.threat_detection'`.
  After implementation, `.venv/bin/pytest tests/test_threat_detection.py`
  passed (3 tests), `.venv/bin/pytest tests/test_wolf_threat.py` passed (10
  tests), and `.venv/bin/pytest tests/test_fox_threat.py` passed (5 tests).
  `make check` passed after formatting/linting, mypy, and all 47 tests.
  `git diff --check` passed. The project interpreter captured four valid JSON
  traces for each corpus: the direct threat was accepted as `true` and produced
  wolf `attack` or fox `flee`; calm, fearful, and ambiguous messages were
  accepted as `false` and produced `do_nothing` for both creatures.
- **Interpretation and limits:** The fixed corpora support this bounded shared
  perception capability: prompt target context does not alter the candidate
  shape or validation, while explicit creature policies retain all action
  authority. Two fixed corpora do not establish general model accuracy or
  certainty calibration.
- **Decision or unresolved question created:** This two-creature result supports
  retaining the small shared detector without a registry or generic actor
  framework. A third materially different perception or policy would need its
  own documented reuse pressure before any broader abstraction is considered.
