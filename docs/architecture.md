# Architecture

This document owns the current verified system design.

## Binary perception pattern

LLM-backed perception is modeled as a sequence of small, independent binary
questions. Each question asks one action-relevant fact about one player message
and a named creature, rather than asking the model to choose an NPC action or
produce a broad interpretation.

For the current threat-detection capability, the question is whether the
message contains a credible hostile threat toward the named creature. The model
returns a boolean answer, a certainty value, and player-text evidence. A `true`
answer is usable only when deterministic validation accepts its exact evidence;
`false`, ambiguity, malformed output, ungrounded evidence, and invalid
certainty all fail closed. Certainty is trace-only and does not change action.

The question and validation capability are reusable. Each creature retains an
explicit deterministic policy that maps an accepted answer to its own action:
the wolf attacks, the fox flees, and all other results do nothing. Future
perceptions should follow this pattern unless a documented decision and evidence
justify a different contract.

## Shared target-aware threat detection

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
but has no policy threshold or branch. The delivery has no creature state,
dialogue, world model, registry, or shared actor framework.

## Two-perception wolf sensemaking

`npc.experiments.food_offer_detection` is a separate binary sensor for whether
a player message explicitly offers food to the wolf. Its candidate and
validation contract mirrors the threat sensor with `food_offer`, `certainty`,
and `evidence`: true evidence must be a non-empty verbatim substring of the
player message, false evidence must be null, and malformed or invalid
candidates fail closed.

`npc.experiments.wolf_sensemaking` invokes the established threat sensor and
the separate food-offer sensor exactly once each for a turn. Its trace retains
each sensor's raw candidate, parsed candidate, and validation result
independently. Only accepted booleans enter the explicit policy: accepted
threat selects `attack`; otherwise accepted food offer selects `approach`;
otherwise it selects `do_nothing`. The `threat_over_food_offer` priority is
fixed and certainty remains trace-only. `python -m npc.experiments.wolf_sensemaking`
loads `scenarios/wolf_sensemaking.yaml`; this bounded wrapper adds no state,
dialogue, world model, registry, or general actor/perception abstraction.
