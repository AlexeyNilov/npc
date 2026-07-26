import asyncio
import json
from dataclasses import replace

import pytest

from npc.composition import CompositionError, replay, run, validate
from npc.experiments.composed_clearing import (
    BASELINE_DECLARATION,
    CAUTIOUS_FOX_DECLARATION,
    FOX_FIRST_RULES_DECLARATION,
    INVALID_FOX_PAIRING_DECLARATION,
    CanonicalState,
)


def test_baseline_composition_records_supplied_components_and_replays_without_actor_mediation() -> None:
    trace = asyncio.run(run(BASELINE_DECLARATION))

    assert trace.declaration.name == "baseline-clearing"
    assert trace.declaration.simulation_name == "hunter-first-clearing-rules"
    assert trace.declaration.actor_names == {"fox": "baseline-fox", "hunter": "baseline-hunter"}
    assert trace.actors["fox"].shown_input == (
        "You are at the edge of a clearing. You smell food in the clearing. The clearing appears quiet."
    )
    assert trace.actors["fox"].proposal == "approach_food"
    assert trace.actors["hunter"].proposal == "set_trap"
    assert trace.resolution.order == ("hunter", "fox")
    assert trace.resolution.outcome == "fox_caught_by_trap"
    assert trace.resulting_state.fox_caught is True
    assert trace.resolution.feedback["fox"] == "A hidden trap catches you as you reach the food."
    json.dumps(trace.as_json(), sort_keys=True)

    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in BASELINE_DECLARATION.actors.values())
    assert replay(BASELINE_DECLARATION, trace) == trace
    assert sum(getattr(actor, "mediation_calls", 0) for actor in BASELINE_DECLARATION.actors.values()) == calls_before


def test_actor_and_rules_substitutions_are_local_and_causally_observable() -> None:
    baseline = asyncio.run(run(BASELINE_DECLARATION))
    cautious = asyncio.run(run(CAUTIOUS_FOX_DECLARATION))
    fox_first = asyncio.run(run(FOX_FIRST_RULES_DECLARATION))

    assert CAUTIOUS_FOX_DECLARATION.simulation is BASELINE_DECLARATION.simulation
    assert CAUTIOUS_FOX_DECLARATION.actors["hunter"] is BASELINE_DECLARATION.actors["hunter"]
    assert cautious.actors["fox"].component_name == "cautious-fox"
    assert cautious.actors["fox"].cognition != baseline.actors["fox"].cognition
    assert cautious.actors["fox"].proposal == "wait"
    assert cautious.resolution.outcome == "waited"

    assert FOX_FIRST_RULES_DECLARATION.actors is BASELINE_DECLARATION.actors
    assert FOX_FIRST_RULES_DECLARATION.initial_state == BASELINE_DECLARATION.initial_state
    assert fox_first.declaration.simulation_name == "fox-first-clearing-rules"
    assert fox_first.resolution.order == ("fox", "hunter")
    assert fox_first.resolution.outcome == "fox_reaches_food"
    assert fox_first.resulting_state.food_consumed is True


def test_structural_pairing_and_withheld_state_boundaries_preserve_provenance() -> None:
    with pytest.raises(CompositionError, match="invalid-fox-pairing.*invalid-fox.*set_trap") as error:
        validate(INVALID_FOX_PAIRING_DECLARATION)
    assert "semantic" not in str(error.value).lower()
    assert "domain" not in str(error.value).lower()

    ready = asyncio.run(run(BASELINE_DECLARATION))
    unavailable = asyncio.run(run(replace(BASELINE_DECLARATION, initial_state=CanonicalState(trap_materials_ready=False))))
    assert "hunter" not in ready.actors["fox"].shown_input.lower()
    assert ready.actors["hunter"].shown_input.endswith("ready.")
    assert unavailable.actors["hunter"].shown_input.endswith("not ready.")
    assert unavailable.resolution.outcome == "fox_reaches_food"


def test_replay_rejects_every_recorded_authority_fact_without_mediation() -> None:
    trace = asyncio.run(run(BASELINE_DECLARATION))
    mutations = (
        replace(trace, declaration=replace(trace.declaration, name="changed")),
        replace(trace, declaration=replace(trace.declaration, proposal_pairings={"fox": ("wait",), "hunter": ("wait",)})),
        replace(trace, initial_state=CanonicalState(trap_materials_ready=False)),
        replace(trace, actors={**trace.actors, "fox": replace(trace.actors["fox"], component_name="changed")}),
        replace(trace, actors={**trace.actors, "fox": replace(trace.actors["fox"], shown_input="changed")}),
        replace(trace, actors={**trace.actors, "fox": replace(trace.actors["fox"], proposal="wait")}),
        replace(trace, resolution=replace(trace.resolution, order=("fox", "hunter"))),
        replace(trace, resolution=replace(trace.resolution, decisions=("changed",))),
        replace(trace, resolution=replace(trace.resolution, transitions=("changed",))),
        replace(trace, resolution=replace(trace.resolution, outcome="changed")),
        replace(trace, resolution=replace(trace.resolution, feedback={"fox": "changed", "hunter": "changed"})),
        replace(trace, resulting_state=CanonicalState()),
    )
    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in BASELINE_DECLARATION.actors.values())
    for mutated in mutations:
        with pytest.raises(CompositionError):
            replay(BASELINE_DECLARATION, mutated)
    assert sum(getattr(actor, "mediation_calls", 0) for actor in BASELINE_DECLARATION.actors.values()) == calls_before
