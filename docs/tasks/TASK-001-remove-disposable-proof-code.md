# TASK-001: Remove disposable proof code

**Status:** Review

**Owner:** Implementer

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `0e46041`

**Depends on:** `None`

**Write scope:** `scenarios/fox_deterministic_utility.yaml`; `scenarios/fox_distance_feedback.yaml`; `scenarios/fox_outcome_rendering.yaml`; and this packet plus `docs/tasks/STATUS.md` for lifecycle handoff only.

**Parallel-safe with:** `None` — this task deletes scenario fixtures in the shared fixture directory.

**Durable information changed:** `What should happen next?` → [Roadmap](../roadmap.md), heading `1. Remove disposable proof code`, at Technical-Lead completion only. No other durable fact changes.

**Simplifier review:** Not required — the task only removes unused fixtures; it adds no boundary, abstraction, or dependency.

## Outcome

The completed beast proof and all of its behavioural coverage remain runnable,
while the three obsolete fox scenario fixtures are absent. The generic LLM chat
utility is deliberately retained for near-term work. This leaves the next
product outcome without unrelated scenario scaffolding.

## Concept provenance

Not applicable. This task removes disposable artifacts and does not add or
change domain information.

## Terminology

Not applicable. No shared term is added, changed, or reused across a boundary.

## Experiment evidence

Not applicable. This is routine cleanup; the existing beast experiment evidence
is preserved and no new experiment claim is made.

## Vision alignment

Not applicable. The task removes scaffolding and does not introduce or claim a
reusable system boundary.

## Canonical context

- [Roadmap](../roadmap.md), `1. Remove disposable proof code`.
- [Requirements](../requirements.md), `First reboot proof`, `LLM-backed perception`, and `Observer inspection and narration`.
- [Architecture](../architecture.md), `Runtime shape`, `Turn processing and authority`, and `Deliberate absences`.
- Initial verification entry point: `tests/test_yaml_beast_proof.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the [Implementer guide](../agent_roles/implementer.md), and only the context named above.

## Task-specific scope

- Delete the three named `scenarios/fox_*.yaml` fixtures.
- Retain `sample/chat.py`, `stream_text`, and all LLM infrastructure unchanged.
- Do not alter beast actors, beast scenarios, simulation logic, requirements,
  architecture, historical evidence, or the next roadmap outcome.

## Acceptance and verification

- The named fox fixtures do not exist.
- `.venv/bin/pytest tests/test_yaml_beast_proof.py` passes, preserving the
  beast proof's authoritative resolution, bounded LLM perception, and
  post-resolution narration coverage.
- `make check` and `git diff --check` pass.

## Stop conditions

- A beast test or documented supported command depends on a proposed deletion.
- Required changes extend beyond the named write scope.
- Unexpected user-owned changes overlap this task's write scope.
- The required verification environment or dependencies are unavailable.

## Handoff

**Status and outcome:** Review — deleted the three obsolete fox scenario fixtures while retaining the beast proof and its coverage.

**Changed files and ownership impact:** Removed `scenarios/fox_deterministic_utility.yaml`, `scenarios/fox_distance_feedback.yaml`, and `scenarios/fox_outcome_rendering.yaml`. These disposable fixtures owned no durable project fact; no canonical owner changed.

**Verification:** Deletion-only configuration change; no artificial failing test applies. `.venv/bin/pytest tests/test_yaml_beast_proof.py` passed (24 passed). `make check` passed. `git diff --check` passed.

**Assumptions, risks, and next action:** Repository search found no references to the removed fixture paths outside this packet. No scope deviations, security risks, or interface changes identified. Technical Lead should inspect the scoped diff and perform Review-to-Done reconciliation.
