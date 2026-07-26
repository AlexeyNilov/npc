# Current Tasks

Technical-Lead-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-001: Bounded causal branching](TASK-001-bounded-causal-branching.md) | Ready | Implementer | Unassigned | None | `src/npc/experiments/composed_clearing.py`, `tests/test_composition.py`, `docs/evidence/2026-07-26-bounded-causal-branching.md`, `docs/requirements.md`, `docs/architecture.md` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
