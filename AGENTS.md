# Agent Instructions

## Repository rules

- Think critically
- No bullshit
- Communicate clearly and in plain language
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

# Token cost optimization

- Do not preload files, directories, role guides for possible
  future use. Latency optimization is not a reason to spend tokens.
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
| What do project-specific terms mean? | [Glossary](docs/glossary.md) |
| How do we reach the vision coherently? | [Strategy](docs/strategy.md) |
| What must the system do? | [Requirements](docs/requirements.md) |
| How does the system work now? | [Architecture](docs/architecture.md) |
| Why was an enduring, project-level consequential choice made? | [Decisions](docs/decisions.md) |
| What should happen next? | [Roadmap](docs/roadmap.md) |
| Why is a choice, assumption, or boundary accepted only for one open outcome? | That outcome in [Roadmap](docs/roadmap.md) |
| What did a bounded experiment demonstrate or refute? | [Experiment evidence](docs/evidence/) |
| What observed problems remain unresolved? | [Issue records](docs/issues/) |
| How do humans/agents build, test, and contribute? | [Contributing](CONTRIBUTING.md) |
| How must agents behave? | [Agent instructions](AGENTS.md) |
| How does work move between roles? | [Agent workflow](docs/agent-workflow.md) |
| How does durable information move between its owners? | [Information flow](docs/information-flow.md) |
| How does this specific role operate? | [Role guides](docs/agent_roles/) |
| What is this assignment? | [Task template](docs/tasks/TEMPLATE.md) |
| Which assignments are currently open? | [Task registry](docs/tasks/STATUS.md) |

Every durable fact must have exactly one owner. Stop when a changed fact has no owner, 
multiple documents claim it, or evidence conflicts with its canonical owner.
