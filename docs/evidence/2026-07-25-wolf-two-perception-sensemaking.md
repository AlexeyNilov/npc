# Experiment: deterministic wolf sensemaking from two grounded perceptions

**Status:** Planned

**Date:** 2026-07-25

**Roadmap outcome:** [Test deterministic sensemaking from two grounded wolf perceptions](../roadmap.md#test-deterministic-sensemaking-from-two-grounded-wolf-perceptions)

## Decision unlocked

Whether two independent validated binary perceptions can feed one explicit,
deterministic wolf-priority choice without introducing a general actor framework,
and whether that choice boundary merits consideration as a durable
sensemaking/intent seam.

## Hypothesis

For one stateless wolf player-message turn, independently validated
player-text-grounded `threat` and `food_offer` perceptions can be combined by a
fixed policy: accepted threat selects `attack`; otherwise an accepted food offer
selects `approach`; otherwise the wolf selects `do_nothing`.

Assumptions: an explicit food offer to the wolf is sufficient for this bounded
experiment; both sensors receive only the player message plus the fixed target;
and the model proposes facts, never an action or priority.

## Observable behavior

A developer can run a checked-in wolf corpus and inspect one JSON trace per
message with both raw candidates, both parsed candidates and validation results,
expected fact/action values, the documented `threat_over_food_offer` priority,
and the deterministic action.

- **Goal:** choose a bounded wolf response from two untrusted player-text facts.
- **Perception:** independent binary threat and explicit-food-offer candidates.
- **Intent or choice:** fixed threat-first deterministic policy over accepted
  booleans only.
- **Action:** `attack`, `approach`, or `do_nothing`.
- **Outcome:** reproducible corpus traces and deterministic fixtures.
- **Feedback or retained history:** none.
- **Later decision affected:** whether this exact priority boundary is a
  candidate durable seam rather than experiment scaffolding.

## Design

- **Authoritative inputs and initial state:** one player-message string and the
  program-controlled target `wolf`; no mutable state. Both model candidates are
  untrusted.
- **Scenario timeline or action contracts:** make one completion call for the
  threat question and one for the explicit-food-offer question; validate each
  candidate independently using exact player-text evidence; pass only accepted
  booleans to a threat-first policy.
- **Expected trace or outputs:** target, case id, player message, expected
  threat/food-offer/action values, two raw candidates, two parsed candidates or
  null, two validation results, priority label, and action.
- **Deliberate exclusions:** world facts, dialogue, memory, outcomes, certainty
  thresholds, LLM-selected actions or conflict resolution, a registry, and a
  generic actor or perception framework.
- **Candidate durable elements and disposable scaffolding:** the explicit
  two-boolean priority policy is the candidate seam; the food-offer sensor,
  corpus, CLI wrapper, and traces are bounded experiment scaffolding unless the
  result supports promotion.

## Signals and stop rule

- **Support signal:** threat-only, offer-only, neither, and both cases expose
  independently accepted facts and deterministically yield `attack`, `approach`,
  `do_nothing`, and threat-priority `attack`; malformed, invalid, ungrounded,
  and certainty-only variants cannot cause an action.
- **Rejection signal:** understanding the corpus requires inferred world facts,
  model-selected actions, ambiguous conflict resolution, or a general framework.
- **Inconclusive condition:** fixtures cannot represent the two facts and their
  conflict independently, or traces cannot show which accepted fact and fixed
  priority caused the action.
- **Stop rule:** complete the fixed corpus and fixtures for each individual
  fact, their conflict, malformed and ungrounded candidates, and certainty
  invariance; then record the result. Do not add memory, dialogue, outcome
  handling, or world machinery.

## Result

Complete at Review.

- **Observed result:** Pending.
- **Reproducibility evidence:** Pending.
- **Interpretation and limits:** Pending.
- **Decision or unresolved question created:** Pending.
- **Canonical follow-up:** Pending.
