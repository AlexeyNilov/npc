# Experiment: deterministic trader offer evaluator

**Status:** Complete

**Date:** 2026-07-25

**Roadmap outcome:** superseded roadmap approach; its observed limits inform
[Outcome 1: Demonstrate one autonomous goal-feedback loop](../roadmap.md#1-demonstrate-one-autonomous-goal-feedback-loop).

## Decision unlocked

Whether the existing trader decision scenario is sufficient evidence for an
actor-model boundary, or should remain a bounded deterministic policy example.

## Hypothesis

An explicit trader and player state plus a bounded offer can be evaluated
deterministically, preserving state invariants and explaining acceptance or
refusal.

**Assumption:** a YAML scenario is a suitable checked-in input for this bounded
experiment.

## Observable behavior

A developer runs `python -m npc.trader_experiment` and sees independent offer
results with a deterministic reason and both resulting states. The checked-in
tests verify accepted transfer, price-limit refusal without state change,
repeatability, independent input states, and conservation on acceptance.

This experiment does not claim autonomous actor behavior. It has no
authoritative time or world event, actor-initiated action, retained feedback, or
later decision changed by history.

## Design

- **Authoritative inputs and initial state:** checked-in trader/player states
  and unit offer prices in `scenarios/trader_decision.yaml`.
- **Scenario timeline or action contracts:** two independent player-initiated
  offers to sell one healing herb: four gold and six gold.
- **Expected trace or outputs:** acceptance at four gold, refusal with
  `price_above_limit` at six gold, and printed resulting states.
- **Deliberate exclusions:** chat, LLMs, persistent history, autonomous action,
  and reusable actor orchestration.
- **Candidate durable elements and disposable scaffolding:** immutable state and
  deterministic policy are evidence for this offer contract only. No shared
  actor-loop boundary is supported.

## Signals and stop rule

- **Support signal:** the documented results and invariants reproduce from
  identical inputs.
- **Rejection signal:** an accepted trade fails to conserve combined herbs or
  gold, a refusal changes state, or identical inputs produce different results.
- **Inconclusive condition:** `None`; this record covers only the bounded offer
  contract, not the broader vision.
- **Stop rule:** do not promote the evaluator into an actor model or add a
  conversational boundary based on this evidence alone.

## Result

- **Observed result:** the current implementation and tests establish the
  bounded deterministic offer behavior described above.
- **Reproducibility evidence:** `python -m npc.trader_experiment`; the trader
  experiment test suite; and the requirements in
  [Requirements](../requirements.md#trader-decision-experiment).
- **Interpretation and limits:** this is evidence for a reproducible,
  player-initiated trade-policy example. It neither supports nor refutes the
  autonomous goal-feedback actor hypothesis.
- **Decision or unresolved question created:** demonstrate an actor-initiated
  decision whose outcome changes a later decision before claiming an actor loop.
- **Canonical follow-up:** [Roadmap Outcome 1](../roadmap.md#1-demonstrate-one-autonomous-goal-feedback-loop).
