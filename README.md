# NPC engine

## Vision

NPC engine aims to become a modular engine for building inspectable simulations
with heterogeneous actors: individuals, groups, organisations, and non-human
systems. The intended user is a simulation builder who needs flexible actor
behaviour without surrendering causal inspection and replay.

Simulation and actor cognition meet through a bounded natural-language
interface. The simulation supplies an actor-accessible substate after enforcing
hard information limits. The actor supplies an epistemic profile—its sensory
limitations, knowledge, worldview, biases, and relevant current context—and
the questions it uses for sensemaking. Generic LLM mediation combines those
inputs into a recorded subjective percept and supports the actor's questions
without requiring its cognition to traverse a simulation-specific schema.
Natural human language is the default semantic intermediary for the target
class of simulations; this is a working product assumption, not a claim that
unstructured language must suit every possible system.

Actor loops interact with a shared authoritative simulation core: they
interpret reality and propose actions, while the simulation core resolves
outcomes and maintains canonical state. Generative components may contribute
through bounded interfaces. A subjective percept may be incomplete or
distorted, but it remains actor-local rather than canonical. Only the simulation
core may commit a canonical transition.

Authoritative causality should be traceable, replayable, and eventually
branchable. Actor behaviour need not always be predictable: controlled
variation may be introduced when the run records its initial state, ordered
inputs, submitted proposals, resolution decisions, and variation results needed
to reproduce its authoritative transitions.

The intended actor loop is:

```text
Authoritative reality
    ↓
Actor-accessible substate + epistemic profile
    ↓
Language-mediated subjective perception
    ↓
Actor-owned questions and sensemaking
    ↓
Intent
    ↓
Action proposal
    ↓
Authoritative resolution
    ↓
Outcome and canonical transition
    ↓
Feedback
    ↙                         ↘
Subjective perception         Sensemaking
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

## Observe an autonomous clearing session

Run the supplied observer-only clearing scenario with a launcher-selected turn
limit:

```bash
python sample/autonomous_clearing.py --turn-limit 3
```

Use `start`, `pause`, `inspect`, `resume`, `replay`, `fresh`, or `exit` at the
terminal prompt. These controls do not select simulation events or actor
actions. The session records each selected event and its causal effects, then
replays that retained history without selecting events or calling a model.

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
