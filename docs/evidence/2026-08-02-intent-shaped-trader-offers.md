# Experiment: Intent-shaped trader decisions over ordered offers

**Status:** Complete

**Date:** 2026-08-02

**Roadmap outcome:** Completed; see the current roadmap.

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
goal; the current balances and offered facts available for its decision; the
shared binary question and validated answer; the resulting accept-or-do-nothing
choice; any proposed buy or sell; the authoritative accepted or rejected
result; and the balances retained as feedback for the next offer.

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
- **Deliberate exclusions:** Reliable intent-dependent answer differences,
  prompt reliability, market modeling, matching, negotiation, other traders,
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

- **Observed result:** The real-LLM run completed all three offers for both
  traders. Each block reported the intent, offer facts, question and validated
  answer, attempted choice, authoritative result, and retained balances. With
  the same starting state and offers, the greedy trader accepted the first two
  offers while the cautious trader rejected all three.
- **Reproducibility evidence:**

```text
.venv/bin/python -m npc.experiments.trader_offers scenarios/trader_offers.yaml
```

Observed trace:

```text
trader: greedy
intent: Build wealth by taking favorable deals.
offer: Buy one apple for four cash.
offer facts: side=buy, item=apple, quantity=1, total price=4
question: Does accepting this offer fit your intent in your current situation?
answer: true
attempted choice: accept offer
authoritative result: accepted
resulting balances:
cash: 6
inventory: apple: 3, gem: 0
trader: greedy
intent: Build wealth by taking favorable deals.
offer: Sell one apple for seven cash.
offer facts: side=sell, item=apple, quantity=1, total price=7
question: Does accepting this offer fit your intent in your current situation?
answer: true
attempted choice: accept offer
authoritative result: accepted
resulting balances:
cash: 13
inventory: apple: 2, gem: 0
trader: greedy
intent: Build wealth by taking favorable deals.
offer: Sell one gem for five cash.
offer facts: side=sell, item=gem, quantity=1, total price=5
question: Does accepting this offer fit your intent in your current situation?
answer: false
attempted choice: do nothing
authoritative result: no transaction proposed
resulting balances:
cash: 13
inventory: apple: 2, gem: 0
trader: cautious
intent: Preserve resources and avoid deals.
offer: Buy one apple for four cash.
offer facts: side=buy, item=apple, quantity=1, total price=4
question: Does accepting this offer fit your intent in your current situation?
answer: false
attempted choice: do nothing
authoritative result: no transaction proposed
resulting balances:
cash: 10
inventory: apple: 2, gem: 0
trader: cautious
intent: Preserve resources and avoid deals.
offer: Sell one apple for seven cash.
offer facts: side=sell, item=apple, quantity=1, total price=7
question: Does accepting this offer fit your intent in your current situation?
answer: false
attempted choice: do nothing
authoritative result: no transaction proposed
resulting balances:
cash: 10
inventory: apple: 2, gem: 0
trader: cautious
intent: Preserve resources and avoid deals.
offer: Sell one gem for five cash.
offer facts: side=sell, item=gem, quantity=1, total price=5
question: Does accepting this offer fit your intent in your current situation?
answer: false
attempted choice: do nothing
authoritative result: no transaction proposed
resulting balances:
cash: 10
inventory: apple: 2, gem: 0
```

- `.venv/bin/pytest tests/test_trader_offers.py`: 13 passed.
- `make check`: formatting, lint, type checking, and all tests passed (37
  passed).
- `git diff --check`: passed.

- **Interpretation and limits:** The run exposes the complete decision and
  authority boundary for both traders, and state persists independently through
  the ordered offers. It also provides one observed intent-linked behavioral
  difference under the recorded profiles: greedy accepted the first two offers,
  while cautious accepted none. This is not evidence that the prompt produces
  that difference reliably across runs, intents, or offers.
- **Decision or unresolved question created:** The bounded
  intent-to-binary-proposal boundary is sufficient for this completed outcome.
  The result does not promote the experiment's trading types or transaction
  contract into reusable system boundaries.
- **Canonical follow-up:** Current mechanism recorded in Architecture; roadmap
  outcome marked Completed.
