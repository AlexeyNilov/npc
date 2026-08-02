# Experiment: Intent-shaped trader decisions over ordered offers

**Status:** Planned

**Date:** 2026-08-02

**Roadmap outcome:** [1. Intent-shaped trader decisions over a sequence of
offers](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers)

## Decision unlocked

Decide whether the smallest intent-to-binary-proposal boundary is sufficient
to carry forward into a later actor-loop outcome, or whether that boundary must
be revised before broader actor behavior is attempted.

## Hypothesis

Given the same starting balances and ordered offers, two traders with different
plain-language intents can each run the complete sequence through a real LLM,
with every request grounded in that trader's current state, while only
deterministic engine resolution changes cash and inventory.

This does not assume or predict that the two intents produce different answers.

## Observable behavior

A developer runs one YAML scenario referencing two YAML actor profiles and
inspects, for both traders and every offer: the intent serving as the actor's
goal; the current balances and offered
facts available for its decision; the shared binary question and validated
answer; the resulting accept-or-do-nothing choice; any proposed buy or sell;
the authoritative accepted or rejected result; and the balances retained as
feedback for the next offer.

## Design

- **Authoritative inputs and initial state:** Separate YAML actor profiles
  define `greedy` and `cautious` traders, their different intents, and their
  shared binary question. One YAML scenario references both profiles and
  defines equal starting cash and inventory plus the same ordered offers. Buy
  and sell are from the trader's perspective; price is the total consideration
  for the offered quantity.
- **Scenario timeline or action contracts:** For each trader, visit each offer
  once in YAML order. One validated binary answer either proposes that exact
  offer or does nothing. The resolver alone checks cash or inventory and
  commits an accepted transaction.
- **Expected trace or outputs:** Each trader-offer block exposes intent, current
  situation, question and answer, attempted choice, authoritative result, and
  resulting balances. A later request reflects earlier accepted state changes.
- **Deliberate exclusions:** Intent-dependent answer differences, prompt
  reliability, market modeling, matching, negotiation, other traders,
  persistence, narration, and a public or reusable trading schema.
- **Candidate durable elements and disposable scaffolding:** The existing
  non-streaming language-model adapter, separate actor/scenario authoring
  boundary, and actor/engine authority principle are durable inputs. Trader
  types, the experiment-local profile and scenario fields, prompt, formatter,
  and transaction mechanics are disposable experiment scaffolding.

## Signals and stop rule

- **Support signal:** A real-LLM run completes both sequences; each request
  contains the correct intent, current balances, and offer; validated answers
  only create proposals; and deterministic resolution alone produces the
  traced next state.
- **Rejection signal:** The trace cannot distinguish LLM choice from
  authoritative resolution, current balances cannot feed the next decision,
  one trader contaminates the other's state, or transaction outcomes depend on
  free-form model output.
- **Inconclusive condition:** Automated contracts pass but a real LLM is
  unavailable or cannot return the bounded answer format, so the required
  end-to-end observation cannot be made.
- **Stop rule:** Stop after one inspectable real-LLM run plus automated coverage
  of input isolation, validation, state feedback, and accepted/rejected
  resolution. Do not tune prompts to force different trader behavior.

## Result

At task Review, complete every field and set the evidence status to `Review`.
The Technical Lead sets the final status after required review and roadmap
closure.

- **Observed result:** Pending.
- **Reproducibility evidence:** Pending.
- **Interpretation and limits:** Pending.
- **Decision or unresolved question created:** Pending.
- **Canonical follow-up:** Pending.
