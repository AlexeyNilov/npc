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
class PlayerState:
    healing_herbs: int
    gold: int


@dataclass(frozen=True)
class Offer:
    name: str
    unit_price_gold: int


@dataclass(frozen=True)
class DecisionResult:
    accepted: bool
    reason: str
    trader_state: TraderState
    player_state: PlayerState


@dataclass(frozen=True)
class TradeProposal:
    offer: Offer
    trader_state: TraderState
    player_state: PlayerState


def evaluate_offer(trader_state: TraderState, player_state: PlayerState, offer: Offer) -> DecisionResult:
    if offer.unit_price_gold > trader_state.max_unit_price_gold:
        return DecisionResult(False, "price_above_limit", trader_state, player_state)

    remaining_gold = trader_state.gold - offer.unit_price_gold
    if trader_state.healing_herbs >= trader_state.target_healing_herbs:
        return DecisionResult(False, "stock_target_met", trader_state, player_state)
    if remaining_gold < trader_state.gold_reserve:
        return DecisionResult(False, "reserve_would_be_breached", trader_state, player_state)

    return DecisionResult(
        accepted=True,
        reason="accepted",
        trader_state=TraderState(
            healing_herbs=trader_state.healing_herbs + 1,
            gold=remaining_gold,
            target_healing_herbs=trader_state.target_healing_herbs,
            max_unit_price_gold=trader_state.max_unit_price_gold,
            gold_reserve=trader_state.gold_reserve,
        ),
        player_state=PlayerState(healing_herbs=player_state.healing_herbs - 1, gold=player_state.gold + offer.unit_price_gold),
    )


def load_scenario(path: Path) -> list[TradeProposal]:
    data = cast(dict[str, object], yaml.safe_load(path.read_text()))
    proposals = cast(list[dict[str, object]], data["proposals"])
    return [
        TradeProposal(
            offer=Offer(
                name=cast(str, proposal["name"]),
                unit_price_gold=cast(int, proposal["unit_price_gold"]),
            ),
            trader_state=TraderState(**cast(dict[str, int], proposal["trader_state"])),
            player_state=PlayerState(**cast(dict[str, int], proposal["player_state"])),
        )
        for proposal in proposals
    ]


def format_state(state: TraderState | PlayerState) -> str:
    return f"healing_herbs={state.healing_herbs}, gold={state.gold}"


def main() -> None:
    scenario_path = Path(__file__).parents[2] / "scenarios" / "trader_decision.yaml"
    for proposal in load_scenario(scenario_path):
        result = evaluate_offer(proposal.trader_state, proposal.player_state, proposal.offer)
        decision = "accepted" if result.accepted else "refused"
        print(
            f"{proposal.offer.name}: price={proposal.offer.unit_price_gold} {decision} ({result.reason}); "
            f"trader: {format_state(result.trader_state)}; player: {format_state(result.player_state)}"
        )


if __name__ == "__main__":
    main()
