import sys
from pathlib import Path
from subprocess import run

from npc.trader_experiment import (
    Offer,
    PlayerState,
    TraderState,
    evaluate_offer,
    load_scenario,
)

ROOT = Path(__file__).parents[1]
SCENARIO_PATH = ROOT / "scenarios" / "trader_decision.yaml"


def test_accepts_an_affordable_offer_and_transfers_one_herb_and_four_gold() -> None:
    trader = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    player = PlayerState(healing_herbs=1, gold=0)

    result = evaluate_offer(trader, player, Offer(unit_price_gold=4))

    assert result.accepted is True
    assert result.reason == "accepted"
    assert result.trader_state == TraderState(
        healing_herbs=1, gold=26, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10
    )
    assert result.player_state == PlayerState(healing_herbs=0, gold=4)


def test_refuses_an_offer_above_the_price_limit_without_either_state_changing() -> None:
    trader = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    player = PlayerState(healing_herbs=1, gold=0)

    result = evaluate_offer(trader, player, Offer(unit_price_gold=6))

    assert result.accepted is False
    assert result.reason == "price_above_limit"
    assert result.trader_state == trader
    assert result.player_state == player


def test_evaluating_the_same_inputs_repeatedly_is_deterministic() -> None:
    trader = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    player = PlayerState(healing_herbs=1, gold=0)
    offer = Offer(unit_price_gold=4)

    assert evaluate_offer(trader, player, offer) == evaluate_offer(trader, player, offer)


def test_checked_in_scenario_cases_start_from_the_same_initial_state() -> None:
    proposals = load_scenario(SCENARIO_PATH)

    assert len(proposals) == 2
    assert all(proposal.trader_state == proposals[0].trader_state for proposal in proposals)
    assert all(proposal.player_state == proposals[0].player_state for proposal in proposals)
    assert proposals[0].trader_state == TraderState(
        healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10
    )
    assert proposals[0].player_state == PlayerState(healing_herbs=1, gold=0)
    assert [proposal.offer.unit_price_gold for proposal in proposals] == [4, 6]


def test_accepted_trade_conserves_combined_healing_herbs_and_gold() -> None:
    trader = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    player = PlayerState(healing_herbs=1, gold=0)

    result = evaluate_offer(trader, player, Offer(unit_price_gold=4))

    assert result.trader_state.healing_herbs + result.player_state.healing_herbs == trader.healing_herbs + player.healing_herbs
    assert result.trader_state.gold + result.player_state.gold == trader.gold + player.gold


def test_cli_prints_each_proposal_decision_reason_and_both_resulting_states() -> None:
    completed = run(
        [sys.executable, "-m", "npc.trader_experiment"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )

    assert "healing herb: price=4 accepted (accepted)" in completed.stdout
    assert "trader: healing_herbs=1, gold=26" in completed.stdout
    assert "player: healing_herbs=0, gold=4" in completed.stdout
    assert "healing herb: price=6 refused (price_above_limit)" in completed.stdout
    assert "trader: healing_herbs=0, gold=30" in completed.stdout
    assert "player: healing_herbs=1, gold=0" in completed.stdout
