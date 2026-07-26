# NPC engine

## Vision

NPC engine is a learning laboratory for discovering how to design autonomous,
deterministic agentic systems. It is the first subgoal toward a future universal
simulation engine: a successful engine should provide lessons and foundations
that can later be carried into that broader effort.

The project explores a general model for **agentic simulated actors**.
Although the first form is an NPC, the model should eventually describe actors
at many scales: individuals, groups, organisations, and non-human systems.

The intended actor loop is:

```text
Reality
    ↓
Perception
    ↓
Sensemaking
    ↓
Intent
    ↓
Action
    ↓
Outcome
    ↓
Feedback
    ↙        ↘
Perception   Sensemaking
```

This is the project's target model, not a claim about the current implementation.

The first audience is the project's developer. The current runnable
demonstration is a deterministic turn loop with LLM-assisted perception and
non-authoritative narration. Its current design is in
[Architecture](docs/architecture.md), its observable behavior is in
[Requirements](docs/requirements.md), and what the utility experiment
established is in [its evidence record](docs/evidence/2026-07-26-fox-deterministic-utility.md).

## Run an interactive turn loop

After installing the project, run:

```bash
python sample/fox_chat.py
```

Each input is an independent player turn. Type `/exit` to quit. Use
`--starting-hunger 0` through `--starting-hunger 100` to choose the initial
hunger value. See [the interactive-turn requirements](docs/requirements.md#interactive-deterministic-fox-utility-turns)
for the command's behavior and state boundaries.

## Project documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Glossary](docs/glossary.md)
- [Decisions](docs/decisions.md)
- [Strategy](docs/strategy.md)
- [Roadmap](docs/roadmap.md)
- [Experiment evidence](docs/evidence/README.md)
- [Development workflow](CONTRIBUTING.md)
