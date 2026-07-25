# TASK-001: Run an inspectable wolf affect-to-action experiment

**Status:** Review

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `40abf03e7c60335b4af849d0513a3a45fc5ef0a3`

**Depends on:** None

**Write scope:** `src/npc/experiments/wolf_affect.py`,
`tests/test_wolf_affect.py`, `scenarios/wolf_affect.yaml`,
`docs/evidence/2026-07-25-wolf-affect-to-action.md`, and the applicable
canonical-owner updates identified at Review.

**Parallel-safe with:** None — this task introduces a new experiment but may
need to update shared canonical documentation at Review.

**Durable information changed:** experiment result ->
`docs/evidence/2026-07-25-wolf-affect-to-action.md` at Review; current verified
implementation -> `docs/architecture.md` at Review; observable behavior ->
`docs/requirements.md` only if accepted as a requirement at Review.

**Simplifier review:** Required — new module-level perception-to-policy boundary
and a candidate reusable interface.

## Outcome

A developer can run a fixed territorial-wolf corpus and inspect, for every
independent message, the raw affect candidate, parsed affect and exact player
text evidence, validation result, expected affect/action pair, and
deterministic `attack` or `do_nothing` action. This makes the LLM's perception
proposal visibly separate from the wolf's authoritative action.

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-07-25-wolf-affect-to-action.md`.
- **Hypothesis and decision unlocked:** an LLM may propose one grounded affect
  reading while deterministic validation and policy alone select the action;
  the result decides whether the next experiment deepens affect, adds small
  creature state, or revises the sensor model.
- **Result handoff:** complete the record at Review, including a negative or
  inconclusive result.

## Vision alignment

- **Vision behavior made observable:** one player message flows from untrusted
  affect perception through deterministic validation to a territorial wolf's
  authoritative action, with no generated reply or state mutation.
- **Classification:** `Disposable experiment scaffolding`.
- **Reuse pressure:** a materially different creature state or action contract
  selected only after the experiment result; not in this task's scope.
- **Boundary rejection signal:** an attack can be produced from malformed or
  ungrounded output, or explaining a corpus result requires trader/world facts
  or non-affect language understanding.

## Canonical context

- [Roadmap: Establish the affect-to-action boundary](../roadmap.md#1-establish-the-affect-to-action-boundary).
- [Decision: Separate LLM semantic interpretation from NPC authority](../decisions.md#2026-07-25-separate-llm-semantic-interpretation-from-npc-authority).
- [Decision: Preserve experiment evidence independently of implementation](../decisions.md#2026-07-25-preserve-experiment-evidence-independently-of-implementation).
- [Architecture: Grounded primary-intent experiment](../architecture.md#grounded-primary-intent-experiment), only as the adapter and trace precedent.
- Initial entry points: `src/npc/experiments/primary_intent.py`,
  `src/npc/infrastructure/language_model.py`, and
  `tests/test_primary_intent.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Create a separate `npc.experiments.wolf_affect` module; do not modify or
  route through the trader or primary-intent modules.
- Use the existing `complete_text` adapter behind an injectable async
  completion callable so offline tests need no network or model.
- Request strict JSON with exactly `affect` and `evidence`. Parse only a JSON
  object with those keys; accept only the labels `hostile`, `non_hostile`, and
  `unclear`, and one non-empty evidence string occurring verbatim in the full
  player message.
- Expose a pure deterministic wolf policy accepting an accepted affect or no
  accepted perception. Its complete mapping is `hostile -> attack` and
  `non_hostile | unclear | rejected -> do_nothing`.
- Add `scenarios/wolf_affect.yaml` with at least one hostile, calm/friendly,
  fearful, and ambiguous message. Each case records its expected affect and
  action. The CLI prints one machine-readable trace per case including those
  expected fields and all observable output fields named above.
- Add no state, dialogue, transaction, world, memory, action, label,
  dependency, general actor framework, or production API.

## Acceptance and verification

- Start with failing behavioral tests proving an accepted grounded hostile
  candidate attacks; accepted grounded `non_hostile` and `unclear` candidates
  do nothing; malformed, unsupported-label, empty-evidence, and ungrounded
  candidates do nothing.
- Test that policy is deterministic from the same accepted perception and that
  the parser rejects key-set/type violations.
- Test every checked-in corpus case's expected affect/action values and a
  mocked-completion trace containing raw candidate, parsed candidate,
  validation, expected pair, and action.
- Confirm the corpus covers hostile, calm/friendly, fearful, and ambiguous
  messages; complete an actual configured-model corpus run only when access is
  available, recording its trace/result in the evidence record.
- Run `pytest`, `make check`, and `git diff --check` after task-local tests.

## Stop conditions

- The corpus needs an affect label, action, state field, or semantic rule not
  named by the roadmap.
- A required acceptance check conflicts with the roadmap or evidence record.
- Implementation would need trader data, world facts, generated dialogue,
  persistent memory, external mutation, a new dependency, or changes outside
  the stated write scope.
- A live model run is unavailable or inconclusive: complete deterministic
  verification, record that condition in the evidence record, and move the
  task to Review rather than compensating with new machinery.

## Handoff

**Status and outcome:** Review — deterministic validation, policy, corpus, and
trace contract are implemented. The configured-model corpus returns grounded
readings; Markdown-fenced JSON is accepted. Its ambiguous case differs from
the expected affect but preserves the expected `do_nothing` action.

**Changed files and ownership impact:** Added disposable wolf experiment code,
fixed corpus, and tests. Updated Requirements with observable wolf behavior,
Architecture with the verified implementation design, and the experiment
evidence record with observed results.

**Verification:** `pytest tests/test_wolf_affect.py` (8 passed); `make check`
(ruff, mypy, and 29 tests passed); `python -m
npc.experiments.wolf_affect` produced the checked-in corpus trace.

**Assumptions, risks, and next action:** Fixture completion verifies the
authority boundary but not model classification quality. The live ambiguous
case needs product/experiment direction before changing the affect contract.
