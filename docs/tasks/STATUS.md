# Current Tasks

Planner-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-004](TASK-004-authoritative-conversation-contract.md) | Planned | Implementer | Unassigned | None | `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`, `README.md`, `docs/{requirements,architecture,decisions}.md` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
