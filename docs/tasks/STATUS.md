# Current Tasks

Planner-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-001](TASK-001-minimal-actor-loop.md) | Ready | Implementer | Unassigned | None | `src/npc/`, `tests/`, `docs/requirements.md`, `docs/architecture.md` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
