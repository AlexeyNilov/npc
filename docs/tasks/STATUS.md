# Current Tasks

Planner-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-001](TASK-001-extract-common-authority-flow.md) | Ready | Implementer | Unassigned | None | `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py` |
| [TASK-002](TASK-002-add-authoritative-identity-capability.md) | Planned | Implementer | Unassigned | TASK-001 | `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`, `docs/requirements.md`, `docs/architecture.md` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
