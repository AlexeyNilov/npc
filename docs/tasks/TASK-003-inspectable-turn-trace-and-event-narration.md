# TASK-003: Inspectable subjective turn trace and event narration

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** 6d338d73a8911534a7d3234455bd180d66acbc38

**Depends on:** None

**Write scope:** `src/npc/simulation.py`, `src/npc/__main__.py`,
`tests/test_yaml_beast_proof.py`,
`docs/evidence/2026-07-28-inspectable-turn-trace-and-event-narration.md`

**Parallel-safe with:** None — all application and focused-test work is in one
small execution path.

**Durable information changed:** bounded experiment result ->
`docs/evidence/2026-07-28-inspectable-turn-trace-and-event-narration.md`.
After acceptance, the Technical Lead reconciles verified behavior with
Requirements, Architecture, and roadmap outcome 3; this task must not edit
those canonical documents.

**Simplifier review:** Required at Review because the task changes the turn
boundary and introduces a model-mediated presentation path.

## Outcome

For every resolved one-beast turn, the CLI presents a compact labelled record
with the validated perception answers, selected bounded proposal, and
authoritative accepted or rejected outcome, followed by clearly labelled
non-authoritative narration. This makes subjective interpretation inspectable
without granting narration control over the simulation.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Validated perception answer | Roadmap outcome 2; `perceive` validation | Exact boolean mapping from declared questions, rendered in the trace only | `perceive` validates; actor profile owns question text | Ephemeral per turn; not retained | Not new |
| Bounded attempted proposal | Roadmap outcome 3; existing `Proposal` | Selected rule's existing bounded proposal, rendered without rule internals | `select_proposal` constructs; `resolve` does not trust it | Ephemeral per turn | Not new |
| Authoritative outcome | Roadmap outcome 3; existing `Outcome` | Resolver's accepted/rejected result, rendered as the outcome section | `resolve` | Returned after each proposal; state already committed only on acceptance | Not new |
| Non-authoritative narration | Roadmap outcome 3; glossary entry | A post-resolution model response derived from completed presentation facts; it is never read by later simulation logic | Narration adapter may create text; it has no state authority | Printed or replaced with an unavailable marker; not retained | Not new |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Non-authoritative narration | Existing glossary entry | CLI presentation and post-resolution model boundary |
| Inspectable turn trace | Packet-local observer-output label | The roadmap fixes its required fields, but this proof does not establish a reusable event-log format |

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-07-28-inspectable-turn-trace-and-event-narration.md`.
- **Hypothesis and decision unlocked:** the record tests whether observer
  inspection and resilient post-resolution narration can build on the bounded
  perception proof without weakening the authority boundary.
- **Result handoff:** complete the record at Review, including a negative or
  inconclusive result, and set its evidence status to `Review`. The Technical
  Lead finalizes the evidence status during completion reconciliation.

## Canonical context

- [Requirements: Observer inspection and narration](../requirements.md#observer-inspection-and-narration).
- [Decision: Use Natural Language as the Default Interface Between Actors and
  the World](../decisions.md#2026-07-26-use-natural-language-as-the-default-interface-between-actors-and-the-world).
- [Roadmap: 3. Inspectable subjective turn trace and entertaining event
  narration](../roadmap.md#3-inspectable-subjective-turn-trace-and-entertaining-event-narration).
- [Architecture: Runtime shape](../architecture.md#runtime-shape), [Turn
  processing and authority](../architecture.md#turn-processing-and-authority),
  and [Resolution contracts](../architecture.md#resolution-contracts).
- Initial source and test entry points: `src/npc/__main__.py`,
  `src/npc/simulation.py`, `src/npc/infrastructure/language_model.py`,
  `tests/test_yaml_beast_proof.py`, `scenarios/beast_perception.yaml`, and
  `actors/beast_perception.yaml`.

Read [AGENTS.md](../../AGENTS.md), this packet, its one role guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Add an immutable, presentation-only turn-record representation or equivalent
  formatter. Its observer-facing output must have stable labelled
  `perception`, `choice`, and `authoritative outcome` sections. `perception`
  contains exactly declared questions and validated boolean answers;
  `choice` identifies the selected rule by its existing observer-facing label
  and renders the bounded attempted proposal; `authoritative outcome` makes
  accepted versus rejected unambiguous. Use deterministic field ordering so
  focused assertions do not depend on mapping order.
- In the CLI turn loop, build and print the trace only after `resolve` returns.
  Preserve the existing rule selection and resolver behavior; a turn without a
  matching rule still produces no resolved-turn record.
- Add a narration operation that runs only after resolution. Its request input
  is a newly constructed, completed presentation payload: the authoritative
  outcome plus only facts needed to describe that outcome (such as the actor,
  accepted action/result, and completed locations or target). It must not
  receive perception answers, the accessible view, rule conditions/order,
  proposal-construction path, resolver controls, mutable `State`, or the raw
  model response from perception.
- Treat a request exception, a non-string response, or blank/whitespace-only
  response as narration unavailable. Print a fixed, clearly labelled
  unavailable marker after the trace; do not retry, fabricate narration,
  alter the returned outcome, or roll back canonical state.
- Keep narration output presentation-only: discard it after printing and do
  not pass it to `perceive`, selection, proposal construction, resolution, or
  a later turn.
- Add focused tests before application changes. With deterministic completion
  doubles, cover an accepted perception-informed move and the existing rejected
  perception-informed `wait` proposal; assert their trace sections preserve
  the subjective/authoritative distinction. Use alternate valid answer
  mappings for the same declared questions to show different selected labels
  and attempted proposals while resolution independently accepts or rejects.
- Capture the narration request and assert it is made after resolution and
  contains only completed presentation facts, not inaccessible content,
  perceptions, rules, proposal controls, or mutable state. Assert narration
  text neither changes committed state nor becomes input to a later turn.
- Cover unavailable and blank narration responses: trace and authoritative
  result remain printed and committed state remains observable. Existing
  perception-failure behavior remains fail-fast before selection or resolution.
- Do not change YAML shapes, actor policy, perception request/validation,
  resolver contracts, `language_model.py`, public interfaces, or canonical
  documentation. Do not add persistence, replay, multi-actor behavior,
  streaming, a general event-log schema, or a general narration prompt/schema
  platform.

## Acceptance and verification

- A CLI run of the beast perception fixture emits one labelled trace for each
  resolved turn followed by a separately labelled non-authoritative narration
  line. The trace alone identifies validated perception, the selected bounded
  choice, and whether resolution accepted or rejected it.
- Focused tests prove the accepted and rejected perception-informed paths, the
  controlled alternate-answer contrast, post-resolution-only narration input,
  and narration-resilience behavior.
- Focused tests also prove narration lacks a route to alter canonical state or
  later-turn input, while existing malformed/unavailable perception tests still
  prove fail-fast behavior before selection and resolution.
- Run, in order:

  ```text
  .venv/bin/python -m pytest -q tests/test_yaml_beast_proof.py
  make check
  git diff --check
  ```

## Stop conditions

- The required presentation payload cannot be defined without exposing hidden
  world content, a raw perception response, rule internals, mutable canonical
  state, or a proposal/resolver control.
- A narration requirement needs a truthfulness guarantee, persistence,
  replay, retry policy, new schema, or later-turn feedback behavior not
  accepted by roadmap outcome 3.
- A needed output field requires a new domain fact, meaning, authority, or
  lifecycle absent from the canonical context.
- Conflicting evidence, unexpected user-owned changes, missing dependency, or
  external mutation required for verification.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
