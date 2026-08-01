# Roadmap

This document owns ordered incomplete outcomes. Completion evidence belongs in
[experiment evidence](evidence/README.md).

## 1. Remove disposable proof code

**Status:** Planned

The repository keeps the completed beast proof and its behavioural coverage,
but removes code and fixtures with no role in that proof or the next product
outcome.

**Observable result:** the beast proof still demonstrates authoritative
resolution, bounded LLM perception, and post-resolution narration; obsolete
fox fixtures.

**Unlocks:** choosing the next product capability without carrying unrelated
experiments forward.

## 2. Intent-shaped trader decisions over a sequence of offers

**Status:** Planned

An observer can run the same YAML-authored sequence of plain-language buy and
sell offers for greedy and cautious traders. Each trader has cash and
inventory. For each offer, an LLM receives the offer, the trader's current
situation, and its intent, then answers the same binary question: whether
accepting the offer fits that intent.

The answer informs an ordinary proposal: accept the offered buy or sell when
true, or do nothing when false. The engine alone accepts or rejects a proposed
transaction and changes cash and inventory. Observer output distinguishes the
perception answer, attempted choice, and authoritative outcome.

**Observable result:** the two traders can process the same offers from the
same starting state while their intent is included in each perception request.
They need not make different decisions in this first proof.

The trader proof should be:
* A YAML-authored sequence of plain-language buy/sell offers with authoritative item, quantity, and price fields.
* A trader has cash, inventory, and an intent: greedy or cautious.
* For every offer, the LLM receives the offer, current cash/inventory, and the trader’s intent.
* Both profiles ask the same binary question: whether accepting the offer fits their intent in their current situation.
* A validated true accepts the offered buy/sell; false proposes doing nothing.
* The engine alone applies or rejects the transaction based on cash and inventory.
* The observer sees the LLM answer, attempted choice, and authoritative outcome.
* The same starting state and offers run for both profiles. Different decisions are welcome but not required in the first proof; proving and improving prompt influence comes later.
