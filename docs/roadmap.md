# Roadmap

This document owns ordered incomplete outcomes. Completion evidence belongs in
[experiment evidence](evidence/README.md).

## 1. Intent-shaped trader decisions over a sequence of offers

**Status:** Completed

This is the next vertical proof of the product model: an actor's intent shapes
its LLM-mediated subjective assessment, but the actor only proposes an action
and the engine remains authoritative.

A YAML scenario supplies an ordered sequence of offers. Each offer has a
plain-language description for the trader to interpret and authoritative
transaction facts: whether it is a buy or sell, the item, quantity, and price.
A trader has an intent, cash, and inventory. The first comparison uses a
`greedy` and a `cautious` trader with the same starting state and the same
offers.

For every offer, the engine supplies the LLM with the offer, the trader's
current cash and inventory, and its intent. Both traders ask the same binary
question: whether accepting the offer fits their intent in their current
situation. A validated `true` lets the trader propose accepting the offered
buy or sell; `false` lets it propose doing nothing. The engine then accepts or
rejects the proposed transaction using the authoritative cash and inventory
state. The observer can see the question and answer, attempted choice, and
authoritative outcome for every offer.

**Observable result:** both traders can run the sequence through a real LLM
and the observer can inspect every decision boundary. The proof must show that
intent is included in the LLM input; it does not need to show that the two
traders make different decisions.

**Boundary:** this proof has no market model, negotiation, other traders, or
claim that the prompt reliably changes LLM behaviour. Prompt effectiveness is
a later question.
