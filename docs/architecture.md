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

## Bounded fox distance feedback

`npc.experiments.fox_distance_feedback` is a fox-only experiment wrapper with
local `TurnTrace`, turn execution, and fixture helpers. Before each turn calls
`perceive_threat`, its authoritative integer starting distance is checked
against the fixed hearing range of `10`. An inaudible turn records no sensor
call and null perception fields; an audible turn calls the shared detector once
and retains its raw candidate, parsed candidate, and validation result.

The wrapper reuses the existing fox `decide_action` policy: only an accepted
grounded threat selects `flee`. Execution is local and deterministic: `flee`
adds the fixed displacement of `5`, while `do_nothing` leaves distance
unchanged. The resulting distance is recorded as feedback and becomes the next
turn's starting distance. `python -m npc.experiments.fox_distance_feedback`
loads only fixture completions from `scenarios/fox_distance_feedback.yaml`; it
does not introduce a generic actor, movement, state, or world abstraction.

## Non-authoritative rendering of completed fox outcomes

`npc.experiments.fox_outcome_rendering` is a fox-only presentation wrapper
around an already completed `fox_distance_feedback.TurnTrace`. It passes its
one-argument fixture renderer a prompt containing only `executed_action` and
explicitly states that rendering neither chooses an action nor asserts a world
fact. The renderer is called once after completion; it cannot receive raw
player text, perception candidate, certainty, distance, or mutable state.

Its local closed JSON contract requires exactly `action` and `message`. Only a
matching completed action and its fixed sentence are accepted: `flee` maps to
`The fox flees.` and `do_nothing` maps to `The fox does nothing.` Malformed,
extra, mismatched, or exceptional results produce the fixed fallback. A frozen
`RenderingTrace` retains the unmodified canonical turn, prompt, raw output or
null, validation result, rendered text, and `non_authoritative=True`; rendered
text has no path to action, distance, feedback, or perception. The module's
YAML fixtures and renderer are disposable scaffolding, not a general renderer,
dialogue, state, or event framework.

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
