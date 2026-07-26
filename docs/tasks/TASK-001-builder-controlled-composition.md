# TASK-001: Builder-controlled composition experiment

**Status:** Ready

**Owner:** Technical Lead

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `79b2781155f7939efbb5bd538118623e9dd22dcf`

**Depends on:** None

**Write scope:** `src/npc/composition.py`; `src/npc/experiments/composed_clearing.py`; `tests/test_composition.py`; `docs/requirements.md`; `docs/architecture.md`; `docs/glossary.md`; `docs/evidence/2026-07-26-builder-controlled-composition.md`; this packet; `docs/tasks/STATUS.md`

**Parallel-safe with:** None — this task establishes the first engine-facing composition boundary and changes its canonical records.

**Durable information changed:**

- What must the system do? -> [Requirements](../requirements.md), new builder-controlled composition heading.
- How does the system work now? -> [Architecture](../architecture.md), new composition mechanism heading.
- What did the bounded experiment demonstrate or refute? -> [Experiment evidence](../evidence/2026-07-26-builder-controlled-composition.md).
- What do project-specific terms mean? -> [Glossary](../glossary.md), `composition declaration` after acceptance.
- Which assignments are currently open? -> [Task registry](STATUS.md).

## Outcome

A project developer can use one readable composition declaration to name a supplied clearing-rules component and supplied fox and hunter actor components, validate their proposal pairings, run, inspect, and replay one shared-world turn. The retained trace names that declaration and its participating supplied components. Replacing only the fox component, and separately only the rules component, produces separately inspectable causal differences without changing generic engine machinery or the unrelated actor.

This is the smallest product-shaped test of independently supplied actors and simulation authority. It matters because later temporal execution and branching need a builder-authored boundary rather than another fixed scenario module.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Component name | [roadmap outcome](../roadmap.md#1-builder-controlled-composition) requires the record to name supplied components. | Builder-provided readable identifier for the supplied actor or simulation component; it has no world-policy meaning. | Builder | Declaration validation -> retained trace -> replay verification | Not new domain meaning. |
| Composition declaration | [roadmap builder workflow](../roadmap.md#builder-workflow) and [accepted composition decision](../decisions.md#2026-07-26-prioritize-builder-controlled-composition). | One builder-owned declaration that names the simulation and actors and explicitly pairs each actor proposal vocabulary with the simulation's accepted vocabulary. | Builder for membership/pairing; engine for structural validation | Validate before run -> retain by value in trace -> replay verification | Shared term; add glossary entry only after accepted behavior exists. |
| Proposal pairing | [decision](../decisions.md#2026-07-26-prioritize-builder-controlled-composition) and existing fox/hunter proposal vocabularies in [requirements](../requirements.md#fox-and-hunter-shared-world-turn). | Structural subset check: every proposal declared by an actor in the composition is accepted for that actor by the selected simulation. It says nothing about semantic compatibility or domain validity. | Engine validates structure; builder owns semantic compatibility; simulation owns admissibility and resolution meaning | Declaration validation -> diagnostic or retained declaration | Not new proposal labels. |
| Baseline and rule-variant resolution order | Existing `hunter` then `fox` order and outcomes in [requirements](../requirements.md#fox-and-hunter-shared-world-turn). | The supplied baseline rules resolve hunter then fox; the supplied replacement rules resolve fox then hunter. Both reuse accepted actors, proposals, canonical fields, transitions, outcomes, and feedback. | Simulation | Supplied rule definition -> authoritative resolution -> retained trace -> replay verification | No new domain label or transition. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Composition declaration | Add a glossary entry after acceptance. | This is the shared builder-to-engine input named by the roadmap and trace contract. |
| Component name | Packet-local structural identifier. | It is trace metadata, not a domain concept. |

## Experiment evidence

- **Evidence record:** [2026-07-26-builder-controlled-composition.md](../evidence/2026-07-26-builder-controlled-composition.md).
- **Hypothesis and decision unlocked:** establish whether this thin builder-facing composition, replacement, trace, and replay boundary can carry into Horizon 2, or whether observed failures require strategic reconsideration.
- **Result handoff:** complete the record at Review, including a negative or inconclusive result, and set its evidence status to `Review`. The Technical Lead finalizes evidence status during completion reconciliation.

## Vision alignment

- **Vision behavior made observable:** a builder supplies independently described actors and a simulation to a common causal execution boundary, then inspects and replays the bounded result.
- **Classification:** `Candidate durable system foundation`.
- **Reuse pressure:** the two required substitutions: a cautious fox actor with unchanged hunter and rules, then fox-first clearing rules with unchanged fox and hunter actors.
- **Boundary rejection signal:** either substitution requires generic-engine or unrelated-component edits, trace/replay cannot derive its result from the recorded declaration and simulation authority, or structural validation must interpret domain meaning.

## Canonical context

- [Roadmap: Builder-controlled composition](../roadmap.md#1-builder-controlled-composition).
- [Strategy: Strategic horizons](../strategy.md#strategic-horizons) and [Target modular composition model](../strategy.md#target-modular-composition-model).
- [Decision: Prioritize builder-controlled composition](../decisions.md#2026-07-26-prioritize-builder-controlled-composition).
- [Requirements: Fox and hunter shared-world turn](../requirements.md#fox-and-hunter-shared-world-turn).
- [Architecture: Fox and hunter shared-world turn](../architecture.md#fox-and-hunter-shared-world-turn).
- Initial source and test entry points: `src/npc/experiments/fox_hunter_shared_world.py`, `tests/test_fox_hunter_shared_world.py`.

## Task-specific scope

- Add a small generic composition module. Its public input is a builder-readable declaration containing a declaration name, one supplied simulation component, and named supplied actor components. It validates proposal pairings before mediation or resolution.
- Keep the generic module domain-opaque: it may validate declared names, actor membership, pairing, trace integrity, and authority-path sequencing, but it must not read clearing-state fields, choose a proposal, interpret a proposal, or decide an outcome.
- Supply a clearing-rules component that owns the accepted existing canonical state, actor-specific observations, accepted proposals, hunter-first baseline resolution, fox-first replacement resolution, feedback, and replay derivation. Supply separate fox and hunter actor components that own their descriptions, subjective cognition, and proposal selection. The rule replacement changes resolution order only; it must reuse existing accepted state and outcome meanings.
- Expose baseline, cautious-fox, and fox-first-rules declarations through the composition surface. The actor replacement changes only the named fox component and declaration; the rule replacement changes only the named simulation component and declaration.
- For a deliberately invalid declaration, use the existing hunter-only `set_trap` proposal in the fox component declaration. The diagnostic must identify the declaration, the named fox component, and the unpaired proposal, while making no semantic or domain-validity claim.
- Retain JSON-safe traces by value: declaration name, participating component names, every actor's shown input and proposal, simulation resolution/feedback, and resulting canonical state. Replay must call no actor mediation and must reject a changed declaration, pairing, actor-visible input, proposal, resolution, feedback, or resulting state.
- Update Requirements and Architecture only with accepted behavior and verified mechanism. Add the glossary entry only after acceptance. Do not change the roadmap, strategy, decision, existing disposable scenario contracts, live-model infrastructure, time semantics, or branching.

## Acceptance and verification

- A focused behavioral test constructs and validates the baseline declaration, runs it, and proves the trace names the declaration and all supplied components; it asserts actor-specific observations/proposals, simulation resolution, feedback, final state, JSON safety, and replay without mediation.
- A source-variation test changes only the supplied fox component/declaration to the cautious fox, retains baseline simulation, hunter, and generic composition module, and observes changed cognition or proposal and authoritative result.
- A source-variation test changes only the supplied rules component/declaration to fox-first rules, retains the baseline fox, hunter, and generic composition module, and observes the changed authoritative resolution/result. It must prove this is a rule-definition substitution rather than an initial-state or parameter change.
- A structural-failure test validates the deliberately mismatched fox vocabulary before run; it asserts an actionable provenance-preserving diagnostic and no claim about semantic compatibility or domain validity.
- Boundary tests prove the engine cannot receive withheld canonical facts through actor inputs; a change to a recorded simulation-owned source fact changes the corresponding actor-visible output or authoritative result as applicable. Tests must not only compare final literals.
- Replay tests mutate each required recorded fact above and assert rejection, while confirming replay makes no mediation request.
- Add a failing focused behavioral test before behavior-changing implementation. Then run `.venv/bin/pytest tests/test_composition.py`, `make check`, and `git diff --check`.

## Stop conditions

- A required component, declaration field, trace field, state field, proposal, transition, outcome, or feedback message has no accepted source, transformation, authority, and lifecycle.
- The implementation needs a new domain rule or semantic compatibility criterion rather than the accepted hunter-first/fox-first contrast; stop and route that decision to the Product Manager.
- The boundary needs time, scheduling, conflict, transport, schema, or branching semantics beyond one bounded turn; stop and route the capability constraint to the Product Strategist.
- A required substitution changes generic engine machinery or an unrelated actor, or a structural diagnostic needs to infer domain semantics.
- Unexpected user-owned changes, unavailable verification, or an unapproved external mutation prevents correct completion.

## Handoff

**Status and outcome:** Ready — one bounded Implementer packet is prepared for
the next ordered roadmap outcome.

**Changed files and ownership impact:** Planning records only: this packet, its registry row, and its planned evidence record. No accepted product behavior or mechanism has changed.

**Verification:** Planning evidence inspected current fixed scenario modules, their behavioral tests, the accepted roadmap/strategy/decision, and repository check targets. No implementation verification has run.

**Assumptions, risks, and next action:** The accepted fox/hunter vocabulary can demonstrate both substitutions without inventing domain semantics. An Implementer can begin test-first with the structural-invalid declaration and three composition declarations, then return the trace, diff, and evidence result for Technical Lead review.
