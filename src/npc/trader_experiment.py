from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml  # type: ignore[import-untyped]


@dataclass(frozen=True)
class TraderState:
    healing_herbs: int
    gold: int
    target_healing_herbs: int
    max_unit_price_gold: int
    gold_reserve: int


@dataclass(frozen=True)
class Offer:
    name: str
    unit_price_gold: int


@dataclass(frozen=True)
class DecisionResult:
    accepted: bool
    reason: str
    state: TraderState


def evaluate_offer(state: TraderState, offer: Offer) -> DecisionResult:
    if offer.unit_price_gold > state.max_unit_price_gold:
        return DecisionResult(accepted=False, reason="price_above_limit", state=state)

    remaining_gold = state.gold - offer.unit_price_gold
    if state.healing_herbs >= state.target_healing_herbs:
        return DecisionResult(accepted=False, reason="stock_target_met", state=state)
    if remaining_gold < state.gold_reserve:
        return DecisionResult(accepted=False, reason="reserve_would_be_breached", state=state)

    return DecisionResult(
        accepted=True,
        reason="accepted",
        state=TraderState(
            healing_herbs=state.healing_herbs + 1,
            gold=remaining_gold,
            target_healing_herbs=state.target_healing_herbs,
            max_unit_price_gold=state.max_unit_price_gold,
            gold_reserve=state.gold_reserve,
        ),
    )


def load_scenario(path: Path) -> tuple[TraderState, list[Offer]]:
    data = cast(dict[str, object], yaml.safe_load(path.read_text()))
    initial_state = cast(dict[str, int], data["initial_state"])
    proposals = cast(list[dict[str, object]], data["proposals"])
    return (
        TraderState(**initial_state),
        [
            Offer(
                name=cast(str, proposal["name"]),
                unit_price_gold=cast(int, proposal["unit_price_gold"]),
            )
            for proposal in proposals
        ],
    )


def format_state(state: TraderState) -> str:
    return f"healing_herbs={state.healing_herbs}, gold={state.gold}"


def main() -> None:
    scenario_path = Path(__file__).parents[2] / "scenarios" / "trader_decision.yaml"
    initial_state, offers = load_scenario(scenario_path)
    for offer in offers:
        result = evaluate_offer(initial_state, offer)
        decision = "accepted" if result.accepted else "refused"
        print(
            f"{offer.name}: price={offer.unit_price_gold} {decision} ({result.reason}); "
            f"resulting state: {format_state(result.state)}"
        )


if __name__ == "__main__":
    main()
