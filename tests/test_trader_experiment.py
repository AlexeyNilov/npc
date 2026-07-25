import sys
from pathlib import Path
from subprocess import run

from npc.trader_experiment import Offer, TraderState, evaluate_offer, load_scenario

ROOT = Path(__file__).parents[1]
SCENARIO_PATH = ROOT / "scenarios" / "trader_decision.yaml"


def test_accepts_an_affordable_offer_and_updates_the_trader_state() -> None:
    state = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)

    result = evaluate_offer(state, Offer(name="four_gold", unit_price_gold=4))

    assert result.accepted is True
    assert result.reason == "accepted"
    assert result.state == TraderState(healing_herbs=1, gold=26, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)


def test_refuses_an_offer_above_the_price_limit_without_a_state_change() -> None:
    state = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)

    result = evaluate_offer(state, Offer(name="six_gold", unit_price_gold=6))

    assert result.accepted is False
    assert result.reason == "price_above_limit"
    assert result.state == state


def test_evaluating_the_same_inputs_repeatedly_is_deterministic() -> None:
    state = TraderState(healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10)
    offer = Offer(name="four_gold", unit_price_gold=4)

    assert evaluate_offer(state, offer) == evaluate_offer(state, offer)


def test_checked_in_scenario_cases_start_from_the_same_initial_state() -> None:
    initial_state, offers = load_scenario(SCENARIO_PATH)

    assert len(offers) == 2
    assert initial_state == TraderState(
        healing_herbs=0, gold=30, target_healing_herbs=3, max_unit_price_gold=5, gold_reserve=10
    )
    assert {offer.name: offer.unit_price_gold for offer in offers} == {"four_gold": 4, "six_gold": 6}


def test_cli_prints_each_proposal_decision_and_resulting_state() -> None:
    completed = run(
        [sys.executable, "-m", "npc.trader_experiment"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )

    assert "four_gold: price=4 accepted (accepted)" in completed.stdout
    assert "healing_herbs=1, gold=26" in completed.stdout
    assert "six_gold: price=6 refused (price_above_limit)" in completed.stdout
    assert "healing_herbs=0, gold=30" in completed.stdout
