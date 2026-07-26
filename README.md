# NPC engine

## Vision

NPC engine aims to become a modular engine for building inspectable simulations
with heterogeneous actors: individuals, groups, organisations, and non-human
systems. The intended user is a simulation builder who needs flexible actor
behaviour without surrendering causal inspection and replay.

Actor loops operate within a shared authoritative simulation substrate: they
interpret reality and propose actions, while the substrate resolves outcomes
and maintains canonical state. Generative components may contribute through
bounded interfaces, but their outputs remain proposals. Only substrate
resolution may commit a canonical transition.

Authoritative causality should be traceable, replayable, and eventually
branchable. Actor behaviour need not always be predictable: controlled
variation may be introduced when the run records its initial state, ordered
inputs, submitted proposals, resolution decisions, and variation results needed
to reproduce its authoritative transitions.

The intended actor loop is:

```text
Authoritative reality
    ↓
Actor-specific perception
    ↓
Sensemaking
    ↓
Intent
    ↓
Action proposal
    ↓
Substrate resolution
    ↓
Outcome and canonical transition
    ↓
Feedback
    ↙        ↘
Perception   Sensemaking
```

This is the project's target model, not a claim about the current implementation.

The project is currently exercised by its developer. The runnable demonstration
is a deterministic fox turn loop with LLM-assisted perception and
non-authoritative narration. Its verified design is in
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
