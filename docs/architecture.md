# Architecture

This document owns the current verified system design.

## Trader decision experiment

`python -m npc.trader_experiment` loads independent proposals from
`scenarios/trader_decision.yaml`. Each proposal contains explicit trader and
player state plus an offered price for one healing herb. `evaluate_offer`
applies the trader's price, stock, and reserve rules and returns the decision
with the resulting immutable states. The command prints each result.

There is no persistence or shared actor-loop runtime. Those concerns are
deferred until a paired decision experiment shows what must survive a meaningful
change in actor goals, actions, or outcomes.

## Grounded primary-intent experiment

`python -m npc.primary_intent_experiment` loads the fixed corpus from
`scenarios/grounded_primary_intent.yaml`. For each independent turn it calls
the configured OpenAI-compatible completion adapter in
`npc.infrastructure.language_model` to propose strict JSON containing one
candidate intent and exact player-text evidence. Deterministic validation
rejects malformed, unsupported, ungrounded, and multi-intent candidates before
only a full-message deterministic parse of a supported healing-herb offer
reaches `evaluate_offer`. The parser, rather than model-proposed fields,
supplies the offer price to the evaluator.

Expressive turns use the same adapter but preserve both authoritative states and
create no memory. An experiment-local policy check blocks generated text that
matches detected canonical facts, commitments, or completed actions. The CLI
prints a JSON trace per turn. This is a bounded experiment, not a general
natural-language framework.
