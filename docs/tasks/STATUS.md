# Current Tasks

Technical-Lead-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-001: Resolve one shared fox-and-hunter world turn](TASK-001-shared-world-turn.md) | Ready | Implementer | Unassigned | None | `src/npc/experiments/fox_hunter_shared_world.py`, `tests/test_fox_hunter_shared_world.py`, `scenarios/fox_hunter_shared_world.yaml` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
