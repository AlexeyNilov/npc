import asyncio
import json
from dataclasses import replace
from typing import Any, cast

import pytest

from npc.composition import CompositionError, replay, replay_timeline, run, run_timeline, validate
from npc.experiments.composed_clearing import (
    BASELINE_DECLARATION,
    CAUTIOUS_FOX_DECLARATION,
    FOX_FIRST_RULES_DECLARATION,
    INVALID_FOX_PAIRING_DECLARATION,
    TWO_STEP_DECLARATION,
    CanonicalState,
    ClearingActor,
    ClearingRules,
    replay_bounded_causal_comparison,
    run_bounded_causal_comparison,
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


def test_two_step_timeline_commits_contextual_exchanges_and_replays_without_mediation() -> None:
    timeline = asyncio.run(run_timeline(TWO_STEP_DECLARATION))

    assert tuple(step.ordinal for step in timeline.steps) == (1, 2)
    first, second = timeline.steps
    assert second.source_state == first.resulting_state
    assert first.actors["fox"].proposal == "wait"
    assert first.actors["hunter"].proposal == "set_trap"
    assert first.resulting_state.trap_set is True
    assert second.actors["fox"].retained_context == "fox:You wait."
    assert second.actors["hunter"].retained_context == "hunter:The fox does not reach the food."
    assert second.actors["fox"].proposal == "approach_food"
    assert second.resolution.order == ("hunter", "fox")
    assert second.resolution.decisions == ("wait", "fox_caught_by_trap")
    assert second.resolution.transitions == ("fox_caught",)
    assert second.resolution.outcome == "fox_caught_by_trap"
    assert second.resolution.feedback["hunter"] == "Your trap catches the fox."
    assert second.resulting_state.fox_caught is True
    json.dumps(timeline.as_json(), sort_keys=True)

    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values())
    assert replay_timeline(TWO_STEP_DECLARATION, timeline) == timeline
    assert sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values()) == calls_before


def test_two_step_inputs_are_state_derived_and_actor_channels_remain_isolated() -> None:
    timeline = asyncio.run(run_timeline(TWO_STEP_DECLARATION))
    unavailable = asyncio.run(
        run_timeline(replace(TWO_STEP_DECLARATION, initial_state=CanonicalState(trap_materials_ready=False)))
    )
    first, second = timeline.steps
    unavailable_first, unavailable_second = unavailable.steps

    assert unavailable_first.actors["hunter"].shown_input.endswith("not ready.")
    assert unavailable_second.resolution.outcome == "fox_reaches_food"
    assert second.actors["fox"].shown_input == first.actors["fox"].shown_input
    assert second.actors["fox"].shown_input != second.actors["hunter"].shown_input
    assert second.actors["fox"].shown_input not in second.actors["hunter"].shown_input
    assert second.actors["hunter"].shown_input not in second.actors["fox"].shown_input
    assert second.actors["fox"].retained_context == "fox:You wait."
    assert second.actors["hunter"].retained_context == "hunter:The fox does not reach the food."
    assert "hunter:" not in second.actors["fox"].retained_context
    assert "fox:" not in second.actors["hunter"].retained_context
    assert first.actors["hunter"].shown_input not in second.actors["fox"].shown_input
    assert first.actors["fox"].shown_input not in second.actors["hunter"].shown_input
    assert first.actors["hunter"].proposal not in second.actors["fox"].shown_input
    assert first.actors["fox"].proposal not in second.actors["hunter"].shown_input
    assert first.actors["hunter"].cognition not in second.actors["fox"].shown_input
    assert first.actors["fox"].cognition not in second.actors["hunter"].shown_input
    assert first.resolution.feedback["hunter"] not in second.actors["fox"].retained_context
    assert first.resolution.feedback["fox"] not in second.actors["hunter"].retained_context
    assert unavailable_first.actors["fox"].proposal == "wait"


def test_each_step_observes_all_actors_before_mediation_and_only_reduces_between_steps() -> None:
    events: list[str] = []
    declaration = replace(
        TWO_STEP_DECLARATION,
        simulation=replace(cast(ClearingRules, TWO_STEP_DECLARATION.simulation), events=events),
        actors={
            name: replace(cast(ClearingActor, actor), mediation_calls=0, events=events)
            for name, actor in TWO_STEP_DECLARATION.actors.items()
        },
    )

    asyncio.run(run_timeline(declaration))

    assert events == [
        "observe:fox",
        "observe:hunter",
        "mediate:fox",
        "mediate:hunter",
        "reduce:fox",
        "reduce:hunter",
        "observe:fox",
        "observe:hunter",
        "mediate:fox",
        "mediate:hunter",
    ]


def test_timeline_replay_rejects_each_recorded_authority_fact_without_mediation() -> None:
    timeline = asyncio.run(run_timeline(TWO_STEP_DECLARATION))
    first, second = timeline.steps
    actor = second.actors["fox"]

    def changed_second(**changes: Any) -> Any:
        return replace(timeline, steps=(first, replace(second, **changes)))

    mutations = (
        replace(timeline, initial_state=CanonicalState(trap_materials_ready=False)),
        replace(timeline, steps=(replace(first, ordinal=3), second)),
        replace(timeline, steps=(replace(first, source_state=CanonicalState(trap_materials_ready=False)), second)),
        changed_second(resulting_state=CanonicalState()),
        changed_second(actors={**second.actors, "fox": replace(actor, retained_context="changed")}),
        changed_second(actors={**second.actors, "fox": replace(actor, shown_input="changed")}),
        changed_second(actors={**second.actors, "fox": replace(actor, proposal="wait")}),
        changed_second(resolution=replace(second.resolution, order=("fox", "hunter"))),
        changed_second(resolution=replace(second.resolution, decisions=("changed",))),
        changed_second(resolution=replace(second.resolution, transitions=("changed",))),
        changed_second(resolution=replace(second.resolution, outcome="changed")),
        changed_second(resolution=replace(second.resolution, feedback={"fox": "changed", "hunter": "changed"})),
    )
    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values())
    for mutated in mutations:
        with pytest.raises(CompositionError):
            replay_timeline(TWO_STEP_DECLARATION, cast(Any, mutated))
    assert sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values()) == calls_before


def test_bounded_causal_comparison_records_one_initial_source_variation_and_replays_independently() -> None:
    comparison = asyncio.run(run_bounded_causal_comparison())

    assert comparison.parent_point == "initial_source_state"
    assert comparison.source_variation == {"trap_materials_ready": (True, False)}
    assert comparison.parent_timeline.initial_state.trap_materials_ready is True
    assert comparison.alternative_timeline.initial_state.trap_materials_ready is False
    assert {
        field: (
            getattr(comparison.parent_timeline.initial_state, field),
            getattr(comparison.alternative_timeline.initial_state, field),
        )
        for field in CanonicalState.__dataclass_fields__
        if getattr(comparison.parent_timeline.initial_state, field)
        != getattr(comparison.alternative_timeline.initial_state, field)
    } == {"trap_materials_ready": (True, False)}
    assert len(comparison.parent_timeline.steps) == len(comparison.alternative_timeline.steps) == 2
    assert comparison.parent_timeline.steps[-1].resolution.outcome == "fox_caught_by_trap"
    assert comparison.alternative_timeline.steps[-1].resolution.outcome == "fox_reaches_food"
    json.dumps(comparison.as_json(), sort_keys=True)

    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values())
    assert replay_bounded_causal_comparison(comparison) == comparison
    assert sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values()) == calls_before


def test_bounded_causal_comparison_rejects_one_field_lineage_and_history_mutations_without_mediation() -> None:
    comparison = asyncio.run(run_bounded_causal_comparison())
    parent = comparison.parent_timeline
    alternative = comparison.alternative_timeline
    changed_parent = replace(
        parent,
        steps=(replace(parent.steps[0], ordinal=3), parent.steps[1]),
    )
    changed_alternative = replace(
        alternative,
        steps=(replace(alternative.steps[0], ordinal=3), alternative.steps[1]),
    )
    mutations = (
        replace(comparison, parent_point="changed"),
        replace(comparison, source_variation={"trap_materials_ready": (False, True)}),
        replace(comparison, parent_timeline=changed_parent),
        replace(comparison, alternative_timeline=changed_alternative),
    )

    calls_before = sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values())
    for mutated in mutations:
        with pytest.raises(CompositionError):
            replay_bounded_causal_comparison(mutated)
    assert sum(getattr(actor, "mediation_calls", 0) for actor in TWO_STEP_DECLARATION.actors.values()) == calls_before


def test_bounded_causal_comparison_keeps_readiness_and_context_hunter_local() -> None:
    comparison = asyncio.run(run_bounded_causal_comparison())
    parent_first = comparison.parent_timeline.steps[0]
    alternative_first, alternative_second = comparison.alternative_timeline.steps

    assert parent_first.actors["hunter"].shown_input.endswith("ready.")
    assert alternative_first.actors["hunter"].shown_input.endswith("not ready.")
    assert alternative_first.actors["hunter"].proposal == "wait"
    assert alternative_first.resulting_state.trap_set is False
    assert all(not step.resulting_state.trap_set for step in comparison.alternative_timeline.steps)
    assert alternative_second.resolution.outcome == "fox_reaches_food"
    for step in comparison.alternative_timeline.steps:
        fox = step.actors["fox"]
        hunter = step.actors["hunter"]
        assert "trap materials" not in fox.shown_input.lower()
        assert "hunter:" not in fox.retained_context
        assert "fox:" not in hunter.retained_context
