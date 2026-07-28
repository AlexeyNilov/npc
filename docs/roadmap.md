# Roadmap

This document owns ordered evidence-bearing outcomes, including completed
milestones retained with their completion evidence. It does not own coding
activities or speculative abstractions.

## 1. YAML-authored authoritative beast simulation

**Status:** Completed

An observer can run a minimal beast scenario defined in YAML and observe narrated
movement, eating, and fleeing in the command line. The outcome proves that
actor-specific capabilities, motivations, and ordered behavioural rules are
separate from the engine, and that scenario content can be changed without
changing engine code.

This comes first because it validates the reboot's core promise of simple,
comprehensible authoring before LLM integration adds another source of
complexity.

Dependencies and assumptions: the initial generic actor and scenario schema
must express the beast without placing beast-specific concepts in the engine.

### Delivery plan and completion evidence

1. Establish the smallest YAML description that can express scenario state,
   an actor profile, ordered behavioural rules, and bounded action proposals.
2. Run that description deterministically from the command line: a rule selects
   a proposal, the engine resolves it, commits the canonical transition, and
   narrates the completed event.
3. Demonstrate a single beast trace covering fleeing from a threat, moving
   toward reachable food, and eating it once reachable. This trace is
   illustrative, not a binding scenario design.
4. Demonstrate YAML-only variation: changing rule order changes the selected
   proposal when food and threat coincide, and changing scenario content changes
   behaviour without engine changes.

Completion evidence shows authoritative resolution and narration for movement,
eating, and fleeing, including rejection of invalid and unsupported proposals.
It also shows that the engine contains no beast-specific policy. Verification:
`make check` and the 9 behavioural tests pass.

Motivations are actor-profile labels in this proof. The result does not show
that motivations independently rank or alter a choice; ordered rules resolve
the demonstrated conflict.

### Run the first proof

After installing development dependencies, run:

```text
.venv/bin/python -m npc scenarios/beast.yaml
```

The command prints the deterministic beast trace. The scenario supplies
canonical initial state and references `actors/beast.yaml`; that profile owns
the beast's ordered rules, capabilities, and motivations. The one-dimensional
location model and YAML document shapes are disposable scaffolding for this
milestone, not a public scenario schema.

### Considerations and boundaries

- This outcome proves one actor and one minimal scenario, not a general
  multi-actor framework or a reusable game model.
- Do not introduce LLM calls, subjective-perception evaluation, generated
  flavour narration, or replay guarantees here. They belong to later outcomes
  or are explicitly out of scope.
- An actor profile may declare binary `perception_questions` for compatibility
  with outcome 2, but outcome 1 does not evaluate them or require an LLM.

## 2. YAML-declared LLM perception for the beast

**Status:** Completed

The same actor profile can declare small binary perception questions. The LLM
answers those questions from the actor-accessible world data, and the actor's
existing behavioural rules use the answers. Canonical world transitions remain
the engine's responsibility.

This follows the authoritative simulation because the perception layer needs a
legible world state, actor boundary, and action-resolution loop to mediate.

Dependency: outcome 1. The LLM's role remains limited to perception; it does
not decide actions or outcomes.

### Product handoff and acceptance evidence

Deliver one bounded beast proof in which the profile declares at least two
binary actor-owned questions and its ordered rules use the resulting answers.
For example, non-binding questions might ask whether a nearby threat requires
fleeing or whether food is reachable. The questions are not action requests.

#### Milestone-specific visibility decision

Outcome 2 must demonstrate an engine-enforced actor-accessible view, but the
first proof has no sensory or spatial model from which to infer one. Therefore,
the scenario declares the minimal subset of its world content visible to the
beast. The builder controls this proof's information boundary in YAML; it is
not a general sensing, visibility, or spatial-observation model.

Before any model call, the engine derives the beast's actor-accessible view
from that declaration. A scenario fixture includes inaccessible content so the
proof can show that the content is absent from the LLM input.

#### Milestone-specific perception-failure decision

The first proof fails fast when the LLM is unavailable or returns a malformed,
incomplete, or non-binary response. It terminates the run with a diagnostic
perception error before that turn selects or resolves a proposal. This exposes
the cause for investigation rather than silently inventing a fallback decision;
fallback perception and recovery behavior are outside this outcome.

For one turn, the engine sends the actor-accessible view and all declared
questions in one LLM request, as required by the accepted natural-language
interface decision. It accepts only the bounded binary-answer contract needed
by the rules. The selected rule still creates only an ordinary bounded action
proposal, and the existing authoritative resolver alone accepts or rejects it
and changes canonical state.

Completion evidence must show all of the following:

1. YAML-only changes to a declared perception question or a rule that uses its
   answer can change the selected beast behaviour.
2. The request contains every declared question and only actor-accessible world
   content.
3. A parsed answer can select a perception-dependent rule, while the LLM has
   no route to select an action, target, destination, resolution result, or
   canonical state transition.
4. The same resolver rejection behavior remains possible after a
   perception-informed proposal.
5. An unavailable LLM or a malformed, incomplete, or non-binary response ends
   the run with a diagnostic perception error before that turn selects or
   resolves a proposal.

This is a useful vertical proof of mediated perception, not evidence of a
reusable perception platform, general visibility model, subjective-state
store, or deterministic replay.

## 3. Inspectable subjective turn trace and entertaining event narration

**Status:** Completed

The command-line observer can follow an entertaining description of each
completed event while also inspecting why the actor attempted it. For every
resolved turn, the output distinguishes the actor's declared perception and
resulting choice from the authoritative outcome. The narration makes the run
pleasant to follow; the labelled trace makes the LLM perception layer and the
authority boundary inspectable.

This follows LLM perception because there must be an actor-specific subjective
view to inspect. It also introduces narration only after an outcome exists, so
the narrator has no opportunity to select an action or influence reality.

Dependency: outcome 2.

### Product handoff

Deliver one bounded beast proof whose observer output contains two deliberately
separate layers for each resolved turn:

1. An **inspectable turn trace** shows the actor-owned question/answer pairs,
   the selected profile rule and its bounded attempted proposal, and the
   authoritative accepted or rejected outcome.
2. A clearly labelled **non-authoritative narration** gives an entertaining
   natural-language description of that completed outcome.

The trace is the inspection record. Narration is presentation only: an observer
must not need to infer facts, causality, acceptance, or rejection from prose.
For example, the trace might show that the beast judged a wolf dangerous,
selected its `flee-threat` rule, and attempted a move; the outcome may then
record acceptance and narration may colourfully describe the retreat. This is
illustrative, not a required wording or output format.

### Delivery plan and completion evidence

1. Define a compact, stable observer-facing turn record with labelled
   `perception`, `choice`, and `authoritative outcome` fields. A perception
   section presents only declared questions and their validated answers; it
   must not reveal inaccessible world content or an unbounded model response.
2. After `resolve` has returned an outcome, provide the narrator only the
   completed outcome and other approved presentation facts. It must receive no
   rule-selection control, proposal construction path, resolver control, or
   writable canonical state.
3. Show an accepted perception-informed beast turn and a perception-informed
   rejected proposal. In both cases, the observer can see the same separation
   between subjective interpretation, attempted choice, and canonical result.
4. Show a causal contrast: alternate valid answers to the same declared
   questions can select different profile rules and attempted proposals, while
   authoritative resolution independently determines the outcome of each.

Completion evidence must show all of the following:

1. The CLI emits a labelled trace for every resolved turn, with validated
   perception answers, selected choice, and an accepted or rejected outcome
   distinguishable without interpreting narration.
2. Narration is requested only after authoritative resolution and is derived
   only from completed presentation input; it cannot cause a proposal,
   acceptance decision, state transition, or later-turn input.
3. A trace for an accepted proposal and one for a rejected proposal preserve
   the subjective/authoritative distinction.
4. A controlled alternate-answer fixture demonstrates that perception can
   alter the displayed choice without granting it authority over outcome.
5. If narration is unavailable or malformed, the resolved outcome and trace
   remain visible and canonical state remains committed. The first proof may
   print a clear narration-unavailable marker rather than retrying or
   fabricating prose.

### Milestone-specific boundaries

- The narration call is post-resolution and non-authoritative. Unlike the
  outcome-2 perception call, narration failure must not erase or fail an
  already resolved turn; this is a deliberate presentation-resilience choice
  limited to this outcome.
- This proof does not establish narrator truthfulness beyond its constrained
  input, deterministic replay, a general event-log format, persisted
  subjective state, streaming interaction, multi-actor narration, or a
  reusable prompt/schema platform.
- Do not expose the actor-accessible view, hidden scenario content, raw model
  responses, or rule internals merely for entertainment. The labelled trace
  is intentionally the smallest information needed to inspect a turn.

### Completion evidence

The CLI now emits deterministic labelled `perception`, `choice`, and
`authoritative outcome` sections for every resolved turn, followed by separately
labelled non-authoritative narration or an unavailable marker. Controlled
perception fixtures demonstrate an accepted `flee` proposal and rejected
`wait` proposal, while narration receives only a completed presentation payload
after resolution. Its failure does not hide the trace or undo committed state.
Verification: the 24 focused behavioral tests and `make check` pass. See
[experiment evidence](evidence/2026-07-28-inspectable-turn-trace-and-event-narration.md).
