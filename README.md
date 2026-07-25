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

This is the project's target model, not a claim about the current
implementation. Experiments should reveal which parts of it must become durable
system structure.

The first audience is the project's developer. The first demonstration is a
D&D/RPG-style trader. It should make choices from its state and goals, retain
relevant history, and refuse deals that do not serve its interests.

The central learning hypothesis is that small, deterministic decision scenarios
can reveal which model elements survive a second, contrasting decision. Both
decisions may belong to the same actor.
Player conversation is a later test of that model, not the current foundation.

## Project documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions.md)
- [Roadmap](docs/roadmap.md)
- [Development workflow](CONTRIBUTING.md)
