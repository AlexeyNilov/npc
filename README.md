# NPC simulation

## Vision

The goal is to create a modular engine for building inspectable simulations
with heterogeneous actors: individuals, groups, organisations, and non-human
systems.

> Instead of writing complex code to translate simulation data into actor actions, an LLM acts as a plain-language bridge between the world and the actor.

* The Simulation engine limits raw world data to only what the actor is allowed to know or see.
* The Actor brings its own persona—its senses, biases, knowledge, and intent.
* The LLM merges the world data and the actor's persona to create their subjective view of reality, answering their questions.

> Actors decide what they want to do based on what they think is happening, but only the central engine decides what actually happens.

## The intended actor loop is:

```text
Authoritative reality
    ↓
Actor-accessible substate + actor profile
    ↓
Language-mediated subjective perception
    ↓
Actor-owned questions and sensemaking
    ↓
Actor intent
    ↓
Actor action proposal
    ↓
Authoritative resolution
    ↓
Outcome and canonical transition
    ↓
Feedback
    ↙                         ↘
Subjective perception         Sensemaking
```

## Project documentation

- [Builder guide: clearing composition experiment](docs/builder-guide.md)
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Glossary](docs/glossary.md)
- [Decisions](docs/decisions.md)
- [Strategy](docs/strategy.md)
- [Roadmap](docs/roadmap.md)
- [Experiment evidence](docs/evidence/README.md)
- [Development workflow](CONTRIBUTING.md)
