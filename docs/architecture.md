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

The current fox policy maps accepted threat to `flee`; all other threat results
do nothing. Future perceptions should follow this pattern unless a documented
decision and evidence justify a different contract.

## Current fox actor-loop mapping

The following maps the intended actor-loop model to the current verified fox
delivery. It identifies the current boundary rather than implying that every
stage is a general engine abstraction.

| Actor-loop stage | What exists now |
| --- | --- |
| Reality | One player-message string and the authoritative distance from the fox. |
| Perception | When the player is within hearing range, two independent LLM-proposed, evidence-grounded sensors assess threat and an explicit food offer. |
| Sensemaking | Deterministic validation accepts or rejects each sensor result, then applies the fixed `threat_over_food_offer` priority. |
| Intent | Not separate yet; the fixed priority policy selects the action directly. |
| Action | The fox deterministically selects and executes `flee`, `approach`, or `do_nothing`. |
| Outcome | Execution produces the resulting authoritative distance. |
| Feedback | That distance becomes the next turn's starting distance. |

Completed outcomes may also receive LLM narration. This is presentation only:
it is outside the authoritative loop and cannot affect action, outcome, or
feedback.

## Bounded fox distance feedback

`npc.experiments.fox_distance_feedback` is a fox-only wrapper with
local `TurnTrace`, turn execution, and fixture helpers. Before each turn calls
`perceive_threat` and `perceive_food_offer`, its authoritative integer starting
distance is checked against the fixed hearing range of `10`. An inaudible turn
records no sensor calls and null perception fields; an audible turn calls each
sensor once and retains its raw candidate, parsed candidate, and
validation result independently.

The fox-local policy gives accepted grounded threat priority: threat selects
`flee`; otherwise accepted grounded food offer selects `approach`; otherwise it
selects `do_nothing`. Execution is local and deterministic: `flee` adds `5`,
`approach` subtracts `3` without going below `1`, and `do_nothing` preserves
distance. The resulting distance is recorded as feedback and becomes the next
turn's starting distance. `python -m npc.experiments.fox_distance_feedback`
loads fixture completions from `scenarios/fox_distance_feedback.yaml`; it does
not introduce a generic actor, movement, state, or world abstraction.

## Non-authoritative rendering of completed fox outcomes

`npc.experiments.fox_outcome_rendering` is a fox-only presentation wrapper
around an already completed `fox_distance_feedback.TurnTrace`. It copies that
frozen turn by value before rendering. Its one-argument narrator receives a
prompt derived only from `executed_action`; it is called once after completion
and cannot receive raw player text, perception candidate, certainty, distance,
or mutable state.

The default command uses an injectable fixture narrator. With
`--configured-narrator`, the module's fox-local adapter makes one
`complete_text` call using the action prompt and a fixed instruction that its
response is non-authoritative presentation, not action selection or world
state. A nonblank response of at most 280 Unicode characters is retained as
arbitrary player-facing narration; blank, oversized, or exceptional responses
produce the fixed fallback. A frozen `RenderingTrace` retains the copied
canonical turn, prompt, raw output or null, validation/failure status, rendered
text, and `non_authoritative=True`; rendered text has no path to action,
distance, feedback, or perception. The module's YAML fixtures and narrator are
disposable scaffolding, not a general renderer, dialogue, state, or event
framework.

## Interactive fox turns

`sample/fox_chat.py` is a terminal loop modeled on the local sample chat,
but it does not stream or roleplay a response. For each player input it calls
the existing `run_turn`, then `render_completed_turn`, prints the resulting
non-authoritative narration, and carries only the canonical feedback distance
to the next iteration. The loop has no conversation history, fox persona, or
path from narration back to the next action.
