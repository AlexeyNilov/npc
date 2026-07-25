# Architecture

This document owns the current verified system design.

## Trader decision experiment

`python -m npc.trader_experiment` loads independent proposals from
`scenarios/trader_decision.yaml`. Each proposal contains explicit trader and
player state plus an offered price for one healing herb. `evaluate_offer`
applies the trader's price, stock, and reserve rules and returns the decision
with the resulting immutable states. The command prints each result.

There is no conversational, language-model, persistence, or shared actor-loop
runtime. Those concerns are deferred until a paired decision experiment shows
what must survive a meaningful change in actor goals, actions, or outcomes.
