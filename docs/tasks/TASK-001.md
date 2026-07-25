# TASK-001: Test deterministic wolf sensemaking from two grounded perceptions

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** 3aeaf52d7439c7f79c45a8efd07fdc60b5e88db7

**Depends on:** None

**Write scope:** `src/npc/experiments/food_offer_detection.py`,
`src/npc/experiments/wolf_sensemaking.py`, `scenarios/wolf_sensemaking.yaml`,
`tests/test_food_offer_detection.py`, `tests/test_wolf_sensemaking.py`,
`docs/evidence/2026-07-25-wolf-two-perception-sensemaking.md`,
`docs/requirements.md`, and `docs/architecture.md`

**Parallel-safe with:** None — the task updates the canonical behavior and
architecture records as well as the experiment evidence.

**Durable information changed:** observable behavior ->
`docs/requirements.md` under a new two-perception wolf section; verified
mechanism -> `docs/architecture.md` under a new two-perception wolf section;
experiment result ->
`docs/evidence/2026-07-25-wolf-two-perception-sensemaking.md`.

**Simplifier review:** Required — the task adds a module and a cross-module
two-sensor boundary; review must reject an unnecessary generic perception or
actor abstraction.

## Outcome

Provide one executable, stateless wolf player-message turn that independently
obtains and validates a threat perception and an explicit-food-offer perception,
then traces the fixed threat-first choice of `attack`, `approach`, or
`do_nothing`. This determines whether the narrow deterministic sensemaking seam
is understandable without a general actor framework.

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-25-wolf-two-perception-sensemaking.md`.
- **Hypothesis and decision unlocked:** use the record's Hypothesis and Decision
  unlocked sections unchanged; complete its Result section at Review for either
  a supporting, rejected, or inconclusive outcome.
- **Result handoff:** include corpus traces and the exact test/check commands;
  do not report a general reusable framework claim.

## Vision alignment

- **Vision behavior made observable:** the perception -> sensemaking -> intent
  portion of one deterministic wolf turn: two narrow, untrusted facts feed a
  deterministic, explainable action choice.
- **Classification:** `Candidate durable system foundation` — only the explicit
  two-boolean priority policy is under test; all sensor, corpus, and CLI
  scaffolding remains disposable.
- **Reuse pressure:** `Not in scope — scaffolding only`; the outcome tests one
  wolf policy, not a second actor or a general framework.
- **Boundary rejection signal:** the implementation needs shared registries,
  inferred world facts, an LLM action/conflict choice, or a generic actor/
  perception framework to make the trace clear.

## Canonical context

- [Roadmap: Test deterministic sensemaking from two grounded wolf perceptions](../roadmap.md#test-deterministic-sensemaking-from-two-grounded-wolf-perceptions).
- [Decision: Keep shared LLM perception separate from creature authority](../decisions.md#2026-07-25-keep-shared-llm-perception-separate-from-creature-authority).
- [Architecture: Binary perception pattern](../architecture.md#binary-perception-pattern) and [Shared target-aware threat detection](../architecture.md#shared-target-aware-threat-detection).
- [Evidence: shared target-aware threat detection](../evidence/2026-07-25-shared-threat-detection.md).
- Initial entry points: `src/npc/experiments/threat_detection.py`,
  `src/npc/experiments/wolf_threat.py`, and `tests/test_wolf_threat.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Preserve `npc.experiments.threat_detection` and the existing wolf/fox threat
  wrappers unchanged. Add a separate explicit-food-offer sensor whose candidate
  shape mirrors the established binary contract with `food_offer`, `certainty`,
  and `evidence`; `true` needs non-empty verbatim player-text evidence and
  `false` needs null evidence.
- Add a dedicated wolf sensemaking wrapper. It must make exactly one call to
  each sensor for a case, retain each raw/parsed/validation result separately,
  and pass only accepted booleans to an explicit function equivalent to
  `attack if threat else approach if food_offer else do_nothing`.
- Add a fixed corpus with threat-only, offer-only, neither, and both cases;
  include expected values for both perceptions, the action, and the fixed
  `threat_over_food_offer` priority. Use fixture completions, not a live model.
- Add failing behavioral tests before application logic for independent prompts
  and validation, each action branch and the both-case priority, malformed and
  ungrounded candidates from either sensor, exactly one call per sensor, and
  certainty invariance.
- At Review, update the three named canonical records only with observed,
  accepted behavior. Do not edit the roadmap, decisions, README, existing
  threat detector, existing wolf/fox corpora, dependencies, or project-wide
  abstractions.

## Acceptance and verification

- The corpus trace independently exposes both candidates, parsed forms,
  validations, expected facts/action, fixed priority, and deterministic action.
- A valid grounded threat alone yields `attack`; a valid grounded explicit food
  offer alone yields `approach`; neither yields `do_nothing`; both yield
  `attack` and show `threat_over_food_offer`.
- A malformed, invalid-certainty, empty-evidence, or ungrounded `true`
  candidate from either sensor is not accepted and cannot cause its associated
  action; a rejected threat cannot suppress an otherwise accepted food offer.
- Changing only valid candidate certainty leaves the action unchanged. Each
  corpus case invokes each sensor once, and neither prompt asks for an action,
  world fact, dialogue, or state.
- Add behavior tests that fail before the application implementation. Run
  `.venv/bin/pytest tests/test_food_offer_detection.py`,
  `.venv/bin/pytest tests/test_wolf_sensemaking.py`, the existing threat test
  modules, `make check`, and `git diff --check`.

## Stop conditions

- Stop if the exact-food-offer question cannot be defined from player text alone,
  or if the fixed threat-first priority is insufficient to decide an observable
  case; return the conflicting message/candidate and the smallest unresolved
  product or authority choice.
- Stop if maintaining separate validations requires changing the established
  threat detector, adding a dependency, or introducing a general actor or
  perception abstraction; return the minimal technical evidence instead.
- Stop for unrelated user-owned changes or any required write outside scope.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
