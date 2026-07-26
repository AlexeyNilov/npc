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

The distance-feedback experiment maps accepted threat to `flee`; all other
threat results do nothing. The utility experiment reuses the same validated
perception contract as an input to deterministic utility scoring. Future
perceptions should follow this narrow, validated pattern unless a documented
decision and evidence justify a different contract.

## Current fox utility actor-loop mapping

The following maps the intended actor-loop model to the current verified fox
delivery. It identifies the current boundary rather than implying that every
stage is a general engine abstraction.

| Actor-loop stage | What exists now |
| --- | --- |
| Reality | One player-message string plus the fox's authoritative distance and hunger. |
| Perception | When the player is within hearing range, two independent LLM-proposed, evidence-grounded sensors assess threat and an explicit food offer. |
| Sensemaking | Deterministic validation accepts or rejects each sensor result; rejected results contribute no utility. |
| Intent | A fox-local deterministic policy scores `flee`, `approach`, and `do_nothing`, then applies its fixed tie order. |
| Action | The fox deterministically selects and executes `flee`, `approach`, or `do_nothing`. |
| Outcome | Execution produces the resulting authoritative distance and advances hunger under the experiment's fixed rule. |
| Feedback | Resulting distance and hunger become the next turn's starting state. |

Completed outcomes may also receive LLM narration. This is presentation only:
it is outside the authoritative loop and cannot affect action, outcome, or
feedback.

## Bounded fox distance feedback

`npc.experiments.fox_distance_feedback` is a fox-only wrapper with
local `TurnTrace`, turn execution, and fixture helpers. Before each turn calls
`perceive_threat` and `perceive_food_offer`, `run_turn` rejects a starting
distance that is not a non-boolean integer greater than or equal to `1` with
`ValueError`. It then checks the authoritative distance against the fixed
hearing range of `10`. An inaudible turn records no sensor calls and null
perception fields; an audible turn calls each sensor once and retains its raw
candidate, parsed candidate, and validation result independently.

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
around an already completed fox turn trace. It copies that frozen turn by value
before rendering. Its one-argument narrator receives a prompt derived from
`executed_action`; a utility turn also supplies its resulting authoritative
hunger as an exact numeric presentation fact only when it is greater than `50`.
It is called once after
completion and cannot receive raw player text, perception candidate, certainty,
distance, or mutable state.

The default command uses an injectable fixture narrator. With
`--configured-narrator`, the module's fox-local adapter makes one
`complete_text` call using the action prompt and a fixed instruction that its
response is best-effort, non-authoritative presentation of only the completed
action. When the prompt includes resulting utility hunger, the narrator must
use it as expressive prose context for food-seeking, but that interpretation is
non-authoritative. The guidance also directs the narrator to avoid unsupported
dialogue, unseen events,
locations, and world state; it does not semantically validate the response. A nonblank response of at most 280
Unicode characters is retained as arbitrary player-facing narration; blank,
oversized, or exceptional responses produce the fixed fallback. A frozen
`RenderingTrace` retains the copied canonical turn, prompt, raw output or null,
validation/failure status, rendered text, and `non_authoritative=True`; rendered
text has no path to action, distance, feedback, or perception. The module's YAML
fixtures and narrator are disposable scaffolding, not a general renderer,
dialogue, state, or event framework.

## Fox deterministic utility experiment

`npc.experiments.fox_deterministic_utility` is a separate fox-local experiment;
it does not change `fox_distance_feedback` or its fixed threat-first policy.
It validates an authoritative starting hunger integer from `0` through `100`,
uses the existing hearing-gated threat and food-offer sensors, and scores only
accepted perceptions. The fixed experiment scores `flee` at `60` for an
accepted threat, `approach` at the starting hunger for an accepted food offer,
and `do_nothing` at `1`; equal scores retain the fixed action order of `flee`,
`approach`, then `do_nothing`. The selected action uses the existing local
distance transition. Each valid completed turn then advances hunger by `10`,
saturating at `100`, for the next turn.

The frozen trace retains the starting and resulting hunger, sensor validation
data, candidate utilities, selected score, tie order, action, and distance
feedback. Its YAML corpus and command-line wrapper are experiment scaffolding,
not a reusable need, utility, actor, or state framework. The experiment's
observed result and limits are owned by
[its evidence record](evidence/2026-07-26-fox-deterministic-utility.md).

## Interactive fox utility turns

`sample/fox_chat.py` is a terminal loop modeled on the local sample chat,
but it does not stream or roleplay a response. For each player input it calls
the fox-local utility `run_turn`, then `render_completed_turn`, prints the
selected action, candidate utilities, and resulting non-authoritative narration
under the `Narration (non-authoritative)` label. It carries only the canonical
feedback distance and resulting hunger to the next iteration. The loop has no
conversation history, fox persona, or path from narration back to the next
action. The renderer can preserve either completed fox trace type, but still
receives only the completed action and, for utility turns, resulting hunger for
narration.
