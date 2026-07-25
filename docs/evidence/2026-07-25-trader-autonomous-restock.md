# Experiment: trader autonomous restock after supplier feedback

**Status:** Planned

**Date:** 2026-07-25

**Roadmap outcome:** [Outcome 1: Demonstrate one autonomous goal-feedback loop](../roadmap.md#1-demonstrate-one-autonomous-goal-feedback-loop)

## Decision unlocked

Whether a small deterministic trader model can demonstrate autonomous,
goal-driven behavior before the project applies reuse pressure or introduces a
shared actor-loop boundary.

## Hypothesis

Given an explicit stock goal and authoritative supplier events, a trader can
initiate a restock action without a player request. Feedback that supplier A
failed to deliver can then deterministically change the trader's later supplier
choice from A to B.

**Assumptions:** a scheduled stock review is a legitimate authoritative world
event; a failed delivery can be represented as feedback without modelling a
general world or economy; supplier reliability is relevant decision state for
this bounded experiment.

## Observable behavior

A developer runs one checked-in timeline and can inspect a deterministic trace
for each step: reality, perception, goal or intent, action, outcome, and
feedback. The first restock action has no player proposal as its trigger. The
later review is replayed with and without the recorded failed-delivery feedback;
those two otherwise identical inputs select different suppliers.

## Design

- **Authoritative inputs and initial state:** the trader begins below its herb
  target, with enough gold to preserve its reserve after either supplier's
  offer. Supplier A offers one herb at four gold; supplier B offers one herb at
  five gold. Without supplier feedback, A is preferred because it is cheaper.
- **Scenario timeline or action contracts:**
  1. A scheduled stock review perceives shortage and the available A offer;
     the trader intends to restore stock and initiates a purchase attempt from
     A.
  2. The authoritative outcome is a failed A delivery. Record that outcome as
     supplier-A failure feedback; do not claim an inventory transfer.
  3. At the next scheduled stock review, A and B offers are available. Compare
     the decision with the failure feedback against an otherwise identical
     replay without it: failure selects B; no feedback selects cheaper A.
- **Expected trace or outputs:** an inspectable causal trace for the initial
  autonomous action and both later-decision branches, plus deterministic final
  state for each branch.
- **Deliberate exclusions:** player chat, LLMs, persistence across a process,
  prices beyond the two fixed offers, general supplier entities, multi-actor
  scheduling, and a reusable actor-loop API.
- **Candidate durable elements and disposable scaffolding:** candidate elements
  are explicit authoritative reality, goal-relevant state, decision record, and
  feedback relevant to a later choice. Supplier names, offers, delivery
  mechanics, output formatting, and any orchestration used only here are
  disposable scaffolding.

## Signals and stop rule

- **Support signal:** identical inputs reproduce each trace; the first action
  is triggered by the scheduled review rather than a player proposal; and the
  only relevant difference in the later comparison is failed-delivery feedback,
  which changes supplier A to supplier B.
- **Rejection signal:** the implementation needs an unstated player request,
  hidden state, a non-authoritative choice, or feedback that does not explain a
  changed later decision.
- **Inconclusive condition:** a valid causal trace is possible only by adding
  general-world, persistence, or framework behavior outside this record's
  scope.
- **Stop rule:** record the result and stop. Do not introduce a shared actor
  loop to force the scenario into a general shape; revise the hypothesis before
  another implementation attempt.

## Result

Complete at Review.

- **Observed result:** Pending.
- **Reproducibility evidence:** Pending.
- **Interpretation and limits:** Pending.
- **Decision or unresolved question created:** Pending.
- **Canonical follow-up:** [Roadmap Outcome 2](../roadmap.md#2-apply-reuse-pressure-with-a-contrasting-decision-contract) if supported; otherwise the roadmap or a decision record.
