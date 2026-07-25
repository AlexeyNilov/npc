# Experiment: wolf affect-to-action boundary

**Status:** Complete

**Date:** 2026-07-25

**Roadmap outcome:** [Establish the affect-to-action boundary](../roadmap.md#1-establish-the-affect-to-action-boundary)

## Decision unlocked

Whether the next experiment should deepen affect perception, add a small
relevant creature state, or revise the perception model.

## Hypothesis

For one player message, an LLM can propose exactly one affect label—`hostile`,
`non_hostile`, or `unclear`—and one exact, non-empty supporting substring from
that message. Deterministic validation can reject every other candidate, and a
wolf policy can map only an accepted `hostile` perception to `attack`.

Assumptions: the configured completion adapter is available for a live corpus
run; fixture completions are sufficient to verify parsing, grounding, and
policy behavior without a model call. This experiment does not test whether a
model's affect judgment is generally correct beyond its fixed corpus.

## Observable behavior

A developer runs a checked-in corpus of independent player messages and can
inspect each message, its expected affect/action pair, raw model candidate,
parsed affect and evidence, validation result, and deterministic wolf action.

- **Goal:** defend the wolf's territorial boundary.
- **Perception:** an untrusted candidate affect plus quoted player-text
  evidence.
- **Intent or choice:** deterministic acceptance or rejection of that
  perception.
- **Action:** `attack` only for an accepted `hostile` perception; otherwise
  `do_nothing`.
- **Outcome:** one inspectable trace per independent corpus case.
- **Feedback or retained history:** none.
- **Later decision affected:** the roadmap's next creature-model pressure.

## Design

- **Authoritative inputs and initial state:** one player-message string; the
  candidate response is untrusted input. The wolf has no mutable state.
- **Scenario timeline or action contracts:** the model returns JSON with
  exactly `affect` and `evidence`. `affect` is one supported label and
  `evidence` is one non-empty string occurring verbatim in the player message.
  A malformed candidate, unsupported label, absent evidence, or ungrounded
  evidence is rejected and yields `do_nothing`.
- **Expected trace or outputs:** JSON includes the corpus case identifier,
  player message, expected affect and action, raw candidate, parsed candidate
  or null, validation result, and action.
- **Deliberate exclusions:** trader facts or state, transactions, world
  simulation, reply generation, multi-intent interpretation, creature memory,
  and actions other than `attack` and `do_nothing`.
- **Candidate durable elements and disposable scaffolding:** the deterministic
  candidate-validation-to-policy seam is a candidate durable element only if a
  later, materially different creature scenario requires it. Prompt text,
  corpus examples, CLI formatting, and module-local types are disposable
  experiment scaffolding.

## Signals and stop rule

- **Support signal:** every accepted fixture candidate cites exact player text;
  accepted hostile candidates always produce `attack`; accepted non-hostile or
  unclear and every rejected candidate produce `do_nothing`; the corpus's
  expected pairs are displayed.
- **Rejection signal:** a candidate causes `attack` without valid text
  evidence, depends on invented world or trader facts, or needs understanding
  beyond affect to explain the result.
- **Inconclusive condition:** model responses for corpus cases do not provide
  enough evidence to assess the label/evidence contract, while deterministic
  fixture verification still passes.
- **Stop rule:** after the fixed corpus, malformed/ungrounded fixtures, and
  deterministic policy tests are run, record the observed result. Do not add
  authority, dialogue, world machinery, memory, labels, or actions to improve
  a result.

## Result

Complete at Review.

- **Observed result:** The checked-in fixtures support the deterministic
  boundary: grounded `hostile` yields `attack`; grounded `non_hostile` and
  `unclear` yield `do_nothing`; malformed, unsupported, empty-evidence, and
  ungrounded candidates yield `do_nothing`. The corpus contains hostile,
  calm/friendly, fearful, and ambiguous messages. A live run returned JSON in
  Markdown fences; parser normalization now accepts that transport wrapper
  while retaining the exact object contract. The hostile, calm, and fearful
  readings matched their expected affects. The ambiguous message was proposed
  as `non_hostile` rather than expected `unclear`; its grounded action was
  still the expected `do_nothing`.
- **Reproducibility evidence:** `python -m npc.experiments.wolf_affect`
  produced one trace per corpus case. `.venv/bin/pytest
  tests/test_wolf_affect.py` passed (8 tests). `make check` passed: ruff
  formatting and lint, mypy, and all 29 tests.
- **Interpretation and limits:** The code and fixtures demonstrate that model
  output cannot select an attack without accepted exact player-text evidence,
  and the policy is replayable from accepted perception. The live trace shows
  the sensor contract works for the corpus, but it does not establish a stable
  distinction between `unclear` and `non_hostile` for ambiguous language.
- **Decision or unresolved question created:** Decide whether the observed
  ambiguous-label mismatch warrants a revised affect contract or a small next
  experiment, without adding state or authority to compensate.
- **Canonical follow-up:** [Roadmap outcome 1](../roadmap.md#1-establish-the-affect-to-action-boundary).
