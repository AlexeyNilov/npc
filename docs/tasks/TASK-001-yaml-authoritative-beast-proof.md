# TASK-001: Run a YAML-authored authoritative beast proof

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `8c79247`

**Depends on:** None

**Write scope:** `src/npc/`, `tests/`, `actors/beast.yaml`, `scenarios/`,
`README.md`, `docs/requirements.md`, `docs/architecture.md`

**Parallel-safe with:** None — this is the first implementation path and may
create the package's initial simulation modules.

**Durable information changed:**

- What is this project, and how do I use it? -> `README.md`, command and
  authoring example.
- What must the system do? -> `docs/requirements.md`, separate reusable actor
  profile and scenario inputs.
- How does the system work now? -> `docs/architecture.md`, only after the
  verified implementation exists.

**Simplifier review:** Required: this task adds the initial command-line and
simulation-module boundaries.

## Outcome

An observer can run one YAML scenario from the command line and read a
deterministic trace in which a beast flees a threat, moves toward food, and
eats it when co-located. The run also shows that the simulation core rejects
an unsupported proposal without committing a transition. The same executable
must demonstrate that swapping the ordered behavioural rules changes the
chosen proposal when threat and food coexist, and that changing scenario
content changes the trace without engine edits.

This is the smallest proof that actor-specific policy is authored in YAML and
the simulation core remains authoritative. It does not establish a reusable
world-model or multi-actor boundary.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Actor profile | Requirements: First reboot proof; Glossary: Actor profile | A separate YAML document supplies capabilities, motivations, and ordered behavioural rules; it never directly mutates canonical state. A scenario references this document. | Builder supplies it; simulation core validates proposals. | Fixed for each run and reusable by another scenario. | Existing meaning; separate-file requirement is owned by Requirements. |
| Action proposal | Roadmap §1; Glossary: Action proposal | A rule yields one bounded structured proposal. The core accepts or rejects it, then alone commits any transition. | Simulation core. | Per turn; discarded after resolution and narration. | Existing meaning. |
| Canonical location | Roadmap §1's movement/reachable-food proof | A disposable one-dimensional location value in YAML. Food is reachable only when it shares the actor's location. A valid move changes only the actor location. | Scenario supplies initial values; simulation core owns changes. | Retained canonical state throughout the run. | Packet-local scaffold, not a glossary term. |
| Consumable food | Requirements: First reboot proof | A scenario entity marked consumable. An eat proposal is valid only when the actor is co-located and has the profile-declared capability required by that proposal; success marks that entity consumed. | Scenario supplies entity data; simulation core validates and commits consumption. | Available until consumed, then retained as consumed state. | `consumable` is packet-local schema spelling; food is requirement vocabulary. |
| Threat | Requirements: First reboot proof | A scenario entity selected by an actor rule; it is not a simulation-core policy. A flee rule produces a generic move-away proposal. | Scenario and actor profile select it; simulation core resolves the resulting movement. | Present for the scenario run. | Existing requirement vocabulary. |
| Rule condition and priority | Requirements: First reboot proof | The actor profile contains an ordered list. The first rule whose generic state predicate matches supplies the proposal; order is the sole conflict resolution for this proof. | Actor profile. | Evaluated once per turn, no retained rule state. | Existing requirement behaviour; predicate field spellings are packet-local. |
| Rejection | Roadmap §1 completion evidence | A proposal outside the declared bounded proposal forms, or failing its authoritative preconditions, produces a narrated rejection and no canonical transition. | Simulation core. | Per resolution; appears in observer output only. | Existing requirement behaviour. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Actor profile | Existing glossary entry | YAML-to-decision boundary. |
| Action proposal | Existing glossary entry | Actor-to-simulation-core boundary. |
| Simulation core | Existing glossary entry | Resolution and canonical-state boundary. |
| location, consumable, rule predicate | Packet-local schema names | Disposable single-scenario scaffolding; do not add glossary entries. |

## Vision alignment

- **Vision behavior made observable:** an actor selects an intent from its
  authored profile, submits an action proposal, and only authoritative
  resolution changes reality and produces observer narration.
- **Classification:** `Disposable experiment scaffolding`
- **Reuse pressure:** a second scenario file must reference the same beast
  profile and change only scenario content to produce a different trace.
- **Boundary rejection signal:** any requirement for a second actor type,
  multiple spatial topologies, or a new action family stops this task rather
  than generalising the scaffold.

## Canonical context

- [Requirements: First reboot proof](../requirements.md#first-reboot-proof)
- [Roadmap: YAML-authored authoritative beast simulation](../roadmap.md#1-yaml-authored-authoritative-beast-simulation)
- [Decision: Natural Language as the Default Interface](../decisions.md#2026-07-26-use-natural-language-as-the-default-interface-between-actors-and-the-world)
- [Glossary: Actor loop terms](../glossary.md#actor-loop-terms)
- Initial source entry point: none; this reboot has no simulation entry point.
- Initial test entry point: none; create behavioural tests under `tests/`.

## Task-specific scope

- Create the smallest Python command-line entry point that accepts a scenario
  path and prints one line for each completed or rejected resolution.
- Load canonical initial entities from a scenario YAML document and its actor
  profile from a separate YAML document referenced by that scenario. Keep both
  document shapes local to `actors/beast.yaml`, `scenarios/`, and the tests;
  do not publish a general schema or compatibility promise.
- Implement only two generic resolution forms: movement and consumption. A
  beast fleeing is a profile-owned rule that submits movement away from a
  selected threat; the core contains no `beast`, `fear`, or policy-specific
  branch.
- Evaluate ordered rules deterministically with generic predicates over the
  supplied scenario state. Profile-declared capabilities must gate the action
  they enable; motivations need only be declared and referenced by rules for
  this proof, not modelled as a numerical utility system.
- Narrate only after the core has accepted or rejected a proposal. Narration is
  deterministic data-derived text, not an LLM call or future-turn input.
- Include two YAML-only variations: a rule-order conflict fixture and a
  changed-content fixture. The variations must reuse engine code.
- Exclude LLM calls, perception evaluation, generated flavour text, replay
  guarantees, a public schema, multiple actors, and migration of pre-reboot
  files.

## Acceptance and verification

Write failing behavioural tests before implementation. At minimum they must
prove the following externally observable contracts:

1. The command-line run prints canonical narration for a deterministic trace
   containing flee, move-toward-food, and eat transitions in that order.
2. An eat proposal before co-location is rejected; its rejection is narrated,
   the food remains available, and no canonical location or consumption state
   changes.
3. An unsupported proposal is rejected and narrated without a canonical
   transition.
4. When food and threat coexist, changing only YAML rule order selects a
   different proposal.
5. Two scenario YAML files referencing the same actor-profile YAML file produce
   different traces when only their scenario content differs; neither run
   requires an engine edit or profile duplication.
6. The core's source has no beast-specific policy term or branch; the profile
   owns threat/food selection and the core only resolves generic movement and
   consumption.

Run task tests first, then `make check` and `git diff --check`. Manually retain
the command output used for the handoff; do not paste raw logs into durable
documentation.

## Stop conditions

- A requested feature requires a second actor, an additional action family,
  a non-linear map, persistence, an LLM, or a public schema.
- A capability, motivation, rule predicate, action proposal, or canonical
  field lacks the provenance and authority recorded above.
- The profile must describe a beast-specific rule in simulation-core code to
  make the trace pass.
- Existing user-owned changes appear in this task's write scope.

## Handoff

**Status and outcome:** Pending implementation.

**Changed files and ownership impact:** Pending.

**Verification:** Pending.

**Assumptions, risks, and next action:** The one-dimensional, co-location
definition of reachability is deliberately disposable proof scaffolding. Assign
this packet to one Implementer; obtain Simplifier review before acceptance.
