# Architecture

This document owns the current verified system design.

## Trader decision experiment

`python -m npc.experiments.trader` loads independent proposals from
`scenarios/trader_decision.yaml`. Each proposal contains explicit trader and
player state plus an offered price for one healing herb. `evaluate_offer`
applies the trader's price, stock, and reserve rules and returns the decision
with the resulting immutable states. The command prints each result.

There is no persistence or shared actor-loop runtime. Those concerns are
deferred until a paired decision experiment shows what must survive a meaningful
change in actor goals, actions, or outcomes.

## Grounded primary-intent experiment

`python -m npc.experiments.primary_intent` loads the fixed corpus from
`scenarios/grounded_primary_intent.yaml`. For each independent turn it calls
the configured OpenAI-compatible completion adapter in
`npc.infrastructure.language_model` to propose strict JSON containing one
candidate intent and exact player-text evidence. Deterministic validation
rejects malformed, unsupported, ungrounded, and multi-intent candidates before
only a full-message deterministic parse of a supported healing-herb offer
reaches `evaluate_offer`. The parser, rather than model-proposed fields,
supplies the offer price to the evaluator.

Expressive turns use the same adapter but preserve both authoritative states and
create no memory. An experiment-local policy check permits only one
non-assertive question and blocks detected trader or world facts, commitments,
or completed actions before rendering a fallback. The CLI prints a JSON trace
per turn. This is a bounded experiment, not a general natural-language
framework.

## Wolf affect-to-action experiment

`python -m npc.experiments.wolf_affect` loads independent cases from
`scenarios/wolf_affect.yaml`. Each case supplies a player message and expected
affect/action pair. The configured completion adapter proposes JSON with only
an affect label and exact player-text evidence. The experiment-local parser
requires the exact key set; deterministic validation accepts only `hostile`,
`non_hostile`, or `unclear` with non-empty evidence occurring verbatim in the
player message. The pure wolf policy maps an accepted `hostile` perception to
`attack` and every other input to `do_nothing`. The command prints a JSON trace
for each case. It creates no creature state, dialogue, world model, or shared
actor framework.

## Shared target-aware threat-detection experiment

`npc.experiments.threat_detection` builds the one target-aware threat prompt,
makes the configured completion call, and parses and validates the common JSON
candidate. Its `perceive_threat` result contains only the raw candidate, parsed
candidate, and validation result; it never selects an action. The exact object
has `threat`, `certainty`, and `evidence`: threat is boolean, certainty is a
finite in-range number, and true evidence is a non-empty verbatim substring of
the player message while false evidence is null.

`python -m npc.experiments.wolf_threat` and
`python -m npc.experiments.fox_threat` load independent cases from
`scenarios/wolf_threat.yaml` and `scenarios/fox_threat.yaml` respectively. Both
call the shared perception module once per case and print a trace with their
target and expected threat/action pair. Their explicit local policies consume
only accepted threat: wolf maps true to `attack`, fox maps true to `flee`, and
false or invalid perception maps to `do_nothing` for both. Certainty is traced
but has no policy threshold or branch. The experiment has no creature state,
dialogue, world model, registry, or shared actor framework.
