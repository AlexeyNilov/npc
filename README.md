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

The first audience is the project's developer. The current demonstrations use a
shared, bounded threat-detection capability: a territorial wolf deterministically
attacks an accepted threat, while a fox deterministically flees one. A fixed
two-turn fox experiment also applies authoritative distance to gate hearing,
executes `flee` as a fixed distance change, and feeds the resulting distance
into the next turn. A completed fox action can then be rendered once by the
configured LLM as arbitrary concise, non-authoritative presentation, or by a
deterministic fallback when narration is unavailable or unusable. The LLM
supplies only an evidence-grounded perception or bounded presentation; it
never chooses an action, determines reachability, or changes distance.

The central learning hypothesis is that small, deterministic decision scenarios
can reveal which model elements survive a second, contrasting decision. Both
decisions may belong to the same actor.
Player conversation, persistent state, and broader actor capabilities are later
tests of that model, not the current foundation.

## Project documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions.md)
- [Roadmap](docs/roadmap.md)
- [Development workflow](CONTRIBUTING.md)
