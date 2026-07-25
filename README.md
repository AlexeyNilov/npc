# NPC engine

## Vision

NPC engine is a learning laboratory for discovering how to design autonomous,
deterministic agentic systems. It is the first subgoal toward a future universal
simulation engine: a successful engine should provide lessons and foundations
that can later be carried into that broader effort.

The project explores a general model for **agentic simulated actors**. Although
the first form is an NPC, the model should be able to describe actors at many
scales: individuals, groups, organisations, and non-human systems. Passive
world entities and fixed systems may provide an actor's reality, but they are
not the primary scope of this project.

An actor continuously participates in this decision loop:

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

The first audience is the project's developer. The first demonstration is a
D&D/RPG-style trader whom a player meets through a simple chat interface. The
trader should be an autonomous economic and social actor: it has inventory and
funds, pursues its own goals, retains relevant history, adapts to the player,
and can refuse deals that do not serve its interests.

The central learning hypothesis is that an actor built around this loop can be
realistic and autonomous enough to remain engaging to a human, rather than
becoming a predictable chat character. Engagement will initially be evaluated
through hands-on play and observation; its precise criteria are intentionally
open for discovery.

The engine should support developers in describing actors. Assisted creation
from natural language, constrained by schemas, is a possible later direction;
it is not the project's initial purpose.

## Project documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions.md)
- [Roadmap](docs/roadmap.md)
- [Development workflow](CONTRIBUTING.md)
