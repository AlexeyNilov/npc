"""Supplied clearing components for the builder-controlled composition experiment."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Literal

from npc.composition import ActorRun, CompositionDeclaration, Resolution

Actor = Literal["fox", "hunter"]


@dataclass(frozen=True)
class CanonicalState:
    fox_location: Literal["clearing_edge", "food"] = "clearing_edge"
    hunter_location: Literal["beside_clearing"] = "beside_clearing"
    hunter_concealed: bool = True
    fox_tracks_lead_to_food: bool = True
    food_available: bool = True
    trap_set: bool = False
    trap_materials_ready: bool = True
    fox_caught: bool = False
    food_consumed: bool = False


@dataclass
class ClearingActor:
    name: str
    actor: Actor
    proposal_vocabulary: tuple[str, ...]
    cognition: str
    proposal: str
    mediation_calls: int = 0

    async def mediate(self, shown_input: str) -> ActorRun:
        self.mediation_calls += 1
        proposal = self.proposal
        if self.actor == "hunter" and "not ready" in shown_input:
            proposal = "wait"
        return ActorRun(self.cognition, proposal)


@dataclass(frozen=True)
class ClearingRules:
    name: str
    resolution_order: tuple[Actor, Actor]

    @property
    def accepted_proposals(self) -> Mapping[str, tuple[str, ...]]:
        return {"fox": ("approach_food", "wait"), "hunter": ("set_trap", "wait")}

    def observe(self, actor: str, canonical_state: CanonicalState) -> str:
        _validate_source_state(canonical_state)
        if actor == "fox":
            return "You are at the edge of a clearing. You smell food in the clearing. The clearing appears quiet."
        if actor == "hunter":
            readiness = "ready" if canonical_state.trap_materials_ready else "not ready"
            return (
                f"You are concealed beside a clearing. Fresh fox tracks lead toward food. Your trap materials are {readiness}."
            )
        raise ValueError("clearing rules have no observation for this actor")

    def resolve(self, canonical_state: CanonicalState, proposals: Mapping[str, str]) -> tuple[CanonicalState, Resolution]:
        _validate_source_state(canonical_state)
        state = canonical_state
        decisions: list[str] = []
        transitions: list[str] = []
        outcome = "waited"
        for actor in self.resolution_order:
            proposal = proposals[actor]
            decisions.append(proposal)
            if actor == "hunter" and proposal == "set_trap" and state.trap_materials_ready:
                state = replace(state, trap_set=True)
                transitions.append("trap_set")
            if actor == "fox" and proposal == "approach_food":
                if state.trap_set:
                    state = replace(state, fox_caught=True)
                    transitions.append("fox_caught")
                    decisions[-1] = "fox_caught_by_trap"
                    outcome = "fox_caught_by_trap"
                    break
                state = replace(state, fox_location="food", food_consumed=True)
                transitions.extend(("fox_moves_to_food", "food_consumed"))
                outcome = "fox_reaches_food"
        feedback = _feedback(outcome)
        return state, Resolution(self.resolution_order, tuple(decisions), tuple(transitions), outcome, feedback)


def _feedback(outcome: str) -> dict[str, str]:
    if outcome == "fox_caught_by_trap":
        return {"fox": "A hidden trap catches you as you reach the food.", "hunter": "Your trap catches the fox."}
    if outcome == "fox_reaches_food":
        return {"fox": "You reach the food.", "hunter": "The fox reaches the food."}
    return {"fox": "You wait.", "hunter": "The fox does not reach the food."}


def _validate_source_state(state: CanonicalState) -> None:
    if (
        state.fox_location != "clearing_edge"
        or state.hunter_location != "beside_clearing"
        or not state.hunter_concealed
        or not state.fox_tracks_lead_to_food
        or not state.food_available
        or state.trap_set
        or state.fox_caught
        or state.food_consumed
    ):
        raise ValueError("clearing rules require the accepted initial clearing state")


BASELINE_FOX = ClearingActor(
    "baseline-fox",
    "fox",
    ("approach_food", "wait"),
    "The clearing seems quiet and the food seems reachable.",
    "approach_food",
)
CAUTIOUS_FOX = ClearingActor(
    "cautious-fox",
    "fox",
    ("approach_food", "wait"),
    "The apparent quiet could conceal danger, so I will wait.",
    "wait",
)
BASELINE_HUNTER = ClearingActor(
    "baseline-hunter",
    "hunter",
    ("set_trap", "wait"),
    "Fresh tracks suggest the fox may approach and my materials are ready.",
    "set_trap",
)
INVALID_FOX = ClearingActor(
    "invalid-fox",
    "fox",
    ("approach_food", "wait", "set_trap"),
    "This component is deliberately structurally invalid.",
    "wait",
)
HUNTER_FIRST_RULES = ClearingRules("hunter-first-clearing-rules", ("hunter", "fox"))
FOX_FIRST_RULES = ClearingRules("fox-first-clearing-rules", ("fox", "hunter"))
BASELINE_ACTORS = {"fox": BASELINE_FOX, "hunter": BASELINE_HUNTER}
PAIRINGS = {"fox": ("approach_food", "wait"), "hunter": ("set_trap", "wait")}

BASELINE_DECLARATION = CompositionDeclaration(
    "baseline-clearing", HUNTER_FIRST_RULES, BASELINE_ACTORS, PAIRINGS, CanonicalState()
)
CAUTIOUS_FOX_DECLARATION = CompositionDeclaration(
    "cautious-fox-clearing", HUNTER_FIRST_RULES, {"fox": CAUTIOUS_FOX, "hunter": BASELINE_HUNTER}, PAIRINGS, CanonicalState()
)
FOX_FIRST_RULES_DECLARATION = CompositionDeclaration(
    "fox-first-clearing", FOX_FIRST_RULES, BASELINE_ACTORS, PAIRINGS, CanonicalState()
)
INVALID_FOX_PAIRING_DECLARATION = CompositionDeclaration(
    "invalid-fox-pairing",
    HUNTER_FIRST_RULES,
    {"fox": INVALID_FOX, "hunter": BASELINE_HUNTER},
    {"fox": ("approach_food", "wait", "set_trap"), "hunter": ("set_trap", "wait")},
    CanonicalState(),
)
