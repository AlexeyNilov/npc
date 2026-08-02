# NPC simulation

## Vision

The goal is to create a modular engine for building inspectable simulations
with heterogeneous actors: individuals, groups, organisations, and non-human
systems.

## Core components

* Scenario
* World
* Actors
* Simulation engine
* Observer

## Key ideas

* Instead of writing complex code to translate simulation data into actor actions, an LLM acts as a plain-language bridge between the world and the actor. It allows to decouple actors from the engine implementation.
* Binary perception pattern: LLM-backed perception is modeled as a sequence of small, independent binary
questions. Each question asks one action-relevant fact, rather than asking the model to choose an NPC action.

## Simulation loop

* World is created from the scenario and follows its rules
* World state is determenistic 
* The Actor brings its own persona - its senses, knowledge, and intent.
* The Simulation engine limits world data to only what the actor is allowed to know.
* The LLM merges the limited world data and the actor's persona to create their subjective view of reality.
* The Actor makes sense of the subjective view by asking LLM questions.

> Actors decide what they want to do based on what they think is happening, but only the simulation engine decides what actually happens.

* Once an action is resolved by the system, an LLM generates a flavor-text description of that event for the observer.
* The LLM only sees completed event data. It cannot alter outcomes, mechanics, or the official world state.

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
