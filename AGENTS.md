# Agent Instructions

## Purpose

Act as an evidence-driven engineering partner. Don't assume. Don't hide confusion. Surface tradeoffs.

## Repository rules

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- Do not preload files, directories, role guides, or chat history for possible
  future use. Latency optimization is not a reason to spend context tokens.
- Search before opening content. Follow real execution paths from named entry
  points and load missing evidence incrementally.

## Route every durable fact by question

Before recording durable information, identify the question it answers. Update
only that question's owner. Other documents link to the owner instead of copying
its content.

Do not preload every document automatically.

| Question | Owner |
| --- | --- |
| What is this project, and how do I use it? | [README](README.md) |
| What must the system do? | [Requirements](docs/requirements.md) |
| How does the system work now? | [Architecture](docs/architecture.md) |
| Why was a consequential choice made? | [Decisions](docs/decisions.md) |
| What should happen next? | [Roadmap](docs/roadmap.md) |
| How do humans/agents build, test, and contribute? | [Contributing](CONTRIBUTING.md) |
| How must agents behave and select roles? | [Agent instructions](AGENTS.md) |
| How does work move between roles? | [Agent workflow](docs/agent-workflow.md) |
| How does this specific role operate? | [Role guides](docs/agent_roles/) |
| What is this assignment? | [Task template](docs/tasks/TEMPLATE.md) |
| Which assignments are currently open? | [Task registry](docs/tasks/STATUS.md) |

Every durable fact has exactly one owner. Top-level product documents under
`docs/` must appear in this table. Git owns superseded history; do not create
archive documents. A new durable document requires a distinct unanswered
question, an ownership-table update, and documentation-contract verification.

Stop when a changed fact has no owner, multiple documents claim it, or evidence
conflicts with its canonical owner.
