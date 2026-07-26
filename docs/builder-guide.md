# Builder guide: the clearing composition experiment

This guide lets you run and modify the completed builder-controlled-composition
experiment. It is a small, deterministic, one-turn sandbox—not a command-line
product surface or a general simulation framework.

Start with:

- `src/npc/experiments/composed_clearing.py`: the supplied fox, hunter, and
  clearing-rules components.
- `src/npc/composition.py`: the domain-opaque validator, runner, trace
  recorder, and replay verifier.

For verified behavior and limits, see the
[composition requirement](requirements.md#builder-controlled-clearing-composition)
and [evidence record](evidence/2026-07-26-builder-controlled-composition.md).

## The basic model

A builder connects actor components to one rules component in a
`CompositionDeclaration`.

```text
builder declaration
  ├─ supplied clearing rules
  ├─ named fox actor
  └─ named hunter actor
          │
          ▼
validate pairings → rules show each actor its allowed input
                  → actors return cognition + proposal
                  → rules resolve proposals and change canonical state
                  → trace is retained
                  → replay verifies the same result without actors running
```

The authority boundary is the important part:

- The **rules** component owns canonical state, what each actor is shown,
  accepted proposals, resolution, feedback, and state changes.
- An **actor** receives only its shown input and returns cognition plus a
  bounded proposal. It cannot commit a world change.
- The **engine** checks declaration structure and records/replays the exchange;
  it does not interpret clearing facts or action meanings.
- The **builder** chooses compatible components and writes their declaration.

## Terms you will see

| Term | In this experiment |
| --- | --- |
| [Builder](glossary.md#product-roles-and-components) | You—the person selecting components and declaring that they belong together. |
| [Composition declaration](glossary.md#product-roles-and-components) | The object that names the rules and actors, lists proposal pairings, and supplies initial state. |
| [Simulation description](glossary.md#product-roles-and-components) | Here, a `ClearingRules` object: it owns the clearing's authoritative behavior. |
| [Actor-accessible substate](glossary.md#actor-loop-terms) | The text shown to an actor. The fox never receives hunter or trap facts. |
| [Action proposal](glossary.md#actor-loop-terms) | A bounded request, such as `approach_food` or `set_trap`; it is not an outcome. |
| [Authoritative](glossary.md#authority-and-state) | Only the supplied rules may turn proposals into state changes and feedback. |
| [Feedback](glossary.md#authority-and-state) | Rules-selected result text for each actor after resolution. |

## First run: baseline

Install development dependencies first if needed:

```bash
make install
```

Then run this from the repository root:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
import asyncio
import json

from npc.composition import replay, run
from npc.experiments.composed_clearing import BASELINE_DECLARATION


async def main() -> None:
    trace = await run(BASELINE_DECLARATION)
    print(json.dumps(trace.as_json(), indent=2, sort_keys=True))
    assert replay(BASELINE_DECLARATION, trace) == trace


asyncio.run(main())
PY
```

In the JSON, look for:

- `declaration`: the declaration name, rules, actor components, and pairings.
- `actors.fox.shown_input`: food and apparent quiet, but no hunter or trap.
- Proposals: fox `approach_food` and hunter `set_trap`.
- Resolution: hunter then fox, producing `fox_caught_by_trap`.
- Replay: it returns the same trace without asking either actor to mediate.

## Compare the supported substitutions

Run the three supplied declarations together:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
import asyncio

from npc.composition import run
from npc.experiments.composed_clearing import (
    BASELINE_DECLARATION,
    CAUTIOUS_FOX_DECLARATION,
    FOX_FIRST_RULES_DECLARATION,
)


async def main() -> None:
    for declaration in (
        BASELINE_DECLARATION,
        CAUTIOUS_FOX_DECLARATION,
        FOX_FIRST_RULES_DECLARATION,
    ):
        trace = await run(declaration)
        print(
            f"{trace.declaration.name}: "
            f"rules={trace.declaration.simulation_name}, "
            f"fox={trace.actors['fox'].component_name}, "
            f"proposal={trace.actors['fox'].proposal}, "
            f"outcome={trace.resolution.outcome}"
        )


asyncio.run(main())
PY
```

| Declaration | What changes | Observable result |
| --- | --- | --- |
| `baseline-clearing` | Nothing | Hunter acts before fox; fox is caught. |
| `cautious-fox-clearing` | Only the named fox component | The fox records different cognition, proposes `wait`, and the turn waits. |
| `fox-first-clearing` | Only the named rules component | Fox resolves before the hunter's trap proposal and reaches food. |

The substitutions are intentionally separate. Do not change the generic runner
or unrelated actor to make one work; that defeats the experiment's main test.

## See structural validation fail safely

The invalid declaration deliberately gives a fox component the hunter-only
`set_trap` proposal. The engine reports that structural mismatch without
guessing whether the components are semantically sensible:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from npc.composition import CompositionError, validate
from npc.experiments.composed_clearing import INVALID_FOX_PAIRING_DECLARATION

try:
    validate(INVALID_FOX_PAIRING_DECLARATION)
except CompositionError as error:
    print(error)
PY
```

The diagnostic names the declaration, supplied component, and unpaired
proposal. It deliberately does not diagnose what `set_trap` means or whether
the scenario is a good idea; those are builder and simulation concerns.

## Make a small actor-only experiment

The simplest safe change is an actor replacement. In a scratch script, create
a fox with the same vocabulary, retain the hunter and rules, and construct a
new declaration:

```python
from npc.composition import CompositionDeclaration
from npc.experiments.composed_clearing import (
    BASELINE_HUNTER,
    CanonicalState,
    ClearingActor,
    HUNTER_FIRST_RULES,
)

curious_fox = ClearingActor(
    name="curious-fox",
    actor="fox",
    proposal_vocabulary=("approach_food", "wait"),
    cognition="The food seems worth the risk, so I will approach.",
    proposal="approach_food",
)

curious_declaration = CompositionDeclaration(
    name="curious-fox-clearing",
    simulation=HUNTER_FIRST_RULES,
    actors={"fox": curious_fox, "hunter": BASELINE_HUNTER},
    proposal_pairings={"fox": ("approach_food", "wait"), "hunter": ("set_trap", "wait")},
    initial_state=CanonicalState(),
)
```

Pass `curious_declaration` to `run()`. Every actor vocabulary must match its
pairing exactly, and every paired proposal must be accepted by the selected
rules for that actor.

## When to change rules instead

Create a rules component only when authoritative behavior changes: actor
visibility, accepted proposals, resolution, state transitions, or feedback.
Keep that domain policy in the supplied rules component, not in
`npc.composition`.

For example, `FOX_FIRST_RULES` differs from `HUNTER_FIRST_RULES` only in
authoritative resolution order. It reuses the same actors and starting state.

## Useful checks

```bash
.venv/bin/pytest tests/test_composition.py
make check
```

The focused test is the fastest way to see the required baseline, replacement,
diagnostic, information-boundary, and replay behavior.

## Current limits

This experiment establishes one bounded clearing turn. It does not yet provide:

- a CLI, GUI, configuration-file format, or plugin system for builders;
- multiple turns, time, scheduling, or persistent scenario execution;
- branching or counterfactual comparison;
- universal world/action schemas;
- engine-level semantic compatibility or domain-validity diagnosis; or
- a live LLM mediation adapter for these supplied components.

Treat it as a concrete place to learn the composition boundary, not a promise
that future simulations will use these exact Python classes or clearing
semantics.

