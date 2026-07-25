# Current Tasks

Planner-only registry of open task packets. Workers receive only their assigned
packet and must not read this registry or sibling packets.

| Task | Status | Role | Agent | Depends on | Write scope |
| --- | --- | --- | --- | --- | --- |
| [TASK-002](TASK-002.md) | Ready | Implementer | Unassigned | None | `src/npc/trader_experiment.py`, `tests/test_trader_experiment.py`, `scenarios/trader_decision.yaml`, `README.md` |

Only Planned, Ready, In progress, Review, or Blocked tasks belong here. Remove
Done packets and rows after integration; Git preserves history.
