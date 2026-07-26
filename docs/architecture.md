# Architecture

This document owns the current verified system design.

For the project-specific vocabulary used below, see the [Glossary](glossary.md).

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
`perceive_threat` and `perceive_food_offer`, `run_turn` validates the starting
distance and uses it to gate perception. It retains each called sensor's raw
candidate, parsed candidate, and validation result independently.

Its fox-local policy selects and executes an action from accepted perceptions;
the resulting distance becomes feedback for the following turn.
`python -m npc.experiments.fox_distance_feedback` loads fixture completions
from `scenarios/fox_distance_feedback.yaml`; it does not introduce a generic
actor, movement, state, or world abstraction. Its observable contract is owned
by [Requirements](requirements.md#bounded-fox-distance-feedback).

## Non-authoritative rendering of completed fox outcomes

`npc.experiments.fox_outcome_rendering` is a fox-only presentation wrapper
around an already completed fox turn trace. It copies that frozen turn by value
before rendering. Its one-argument narrator receives a prompt derived from the
completed action and selected presentation facts. It is called after completion
and cannot receive raw player text, perception candidate, certainty, distance,
or mutable state.

The default command uses an injectable fixture narrator. With
`--configured-narrator`, the module's fox-local adapter makes one
`complete_text` call using the action prompt and a fixed instruction that its
response is best-effort, non-authoritative presentation. Validation preserves
the canonical turn and uses a deterministic fallback when needed. A frozen
`RenderingTrace` retains the copied canonical turn, prompt, raw output or null,
validation/failure status, rendered text, and `non_authoritative=True`; rendered
text has no path to action, distance, feedback, or perception. The module's YAML
fixtures and narrator are disposable scaffolding, not a general renderer,
dialogue, state, or event framework. Its observable contract is owned by
[Requirements](requirements.md#non-authoritative-rendering-of-completed-fox-outcomes).

## Fox deterministic utility experiment

`npc.experiments.fox_deterministic_utility` is a separate fox-local experiment;
it does not change `fox_distance_feedback` or its fixed threat-first policy.
It combines the existing hearing-gated perceptions with authoritative hunger to
select and execute a fox action, then carries distance and hunger into the next
turn.

The frozen trace retains the starting and resulting hunger, sensor validation
data, candidate utilities, selected score, tie order, action, and distance
feedback. Its YAML corpus and command-line wrapper are experiment scaffolding,
not a reusable need, utility, actor, or state framework. The experiment's
observable contract is owned by
[Requirements](requirements.md#deterministic-fox-utility-turns); its observed
result and limits are owned by [its evidence record](evidence/2026-07-26-fox-deterministic-utility.md).

## Interactive fox utility turns

`sample/fox_chat.py` is a terminal loop modeled on the local sample chat,
but it does not stream or roleplay a response. For each player input it calls
the fox-local utility `run_turn`, then `render_completed_turn`. It carries only
canonical feedback distance and resulting hunger to the next iteration. The
loop has no conversation history, fox persona, or path from narration back to
the next action. The renderer can preserve either completed fox trace type, but
still receives only completed presentation facts. Its observable command
contract is owned by
[Requirements](requirements.md#interactive-deterministic-fox-utility-turns).

## Builder-controlled clearing composition

`npc.composition` provides the narrow, domain-opaque execution boundary for
this experiment. A `CompositionDeclaration` carries a builder-selected
simulation, named actors, their explicit proposal pairings, and source state.
The engine validates membership and proposal-subset structure, asks the
simulation for each actor's input before mediation, records actor outputs, and
then asks the simulation to resolve the collected proposals. It does not read
clearing fields or interpret proposals and outcomes. Actor output contains
only cognition and a proposal; the trace's shown input is the engine-retained,
simulation-derived value rather than actor-controlled data.

`run_timeline` extends that boundary through exactly two steps without changing
the one-turn `run` contract. It records `StepRecord` values within a
`CompositionTimeline`; each includes an ordinal, source and resulting state,
actor exchange records, and simulation resolution. Stateful actors declare an
initial context, a context-aware mediation method, and a deterministic reducer.
The engine gives the reducer only that actor's prior context and own selected
feedback, then carries its result into the next actor exchange. `replay_timeline`
re-derives inputs and resolutions and applies those reducers without mediation.

The same clearing experiment adds a disposable `BoundedCausalComparison`
record around two invocations of that existing fixed-two-step path. Its parent
uses `TWO_STEP_DECLARATION`; its separately declared alternative changes only
the initial `trap_materials_ready` value to `false`. The comparison replayer
checks the fixed parent label and variation, then delegates each history to
`replay_timeline`, preserving actor-free verification without adding branch
semantics to `npc.composition`.

`npc.experiments.composed_clearing` supplies the experiment's clearing actors
and hunter-first or fox-first rule components. The supplied rules alone derive
observations, own accepted proposal vocabularies, and apply canonical
transitions and feedback. The two-step fixture owns its limited trap-set
continuation; it is not generic clearing lifecycle policy. This establishes
neither temporal scheduling nor a universal world or proposal schema. Its
observable contract is owned by
[Requirements](requirements.md#builder-controlled-clearing-composition).

## Autonomous observer clearing session

`npc.experiments.autonomous_clearing` is a separate, scenario-local terminal
runtime. A launcher supplies a validated turn limit and the session advances
automatically to its ending, printing each completed causal account alongside
the retained actor-cognition and narration prompt/raw-response pairs. After the
ending, the observer can inspect completed causal records, replay a completed
session, or begin a fresh one. The observer supplies no causal input.

Each turn records the selected event before its effect, actor-filtered
observations and actor-local feedback, non-authoritative LLM cognition,
deterministic proposals, hunter-first resolution, state, ending, and
non-authoritative narration. The scenario owns both event selection and
resolution. Replay re-derives authoritative history from retained event values
and does not invoke event selection, actor cognition, or narration. This is a
disposable clearing session, not a general event, scheduling, persistence, or
presentation framework. Its observable contract is owned by
[Requirements](requirements.md#autonomous-observer-clearing-session).
