import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import cast

import pytest

from npc.experiments.fox_deterministic_utility import (
    HEARING_RANGE,
    load_corpus,
    run_fixture,
    run_turn,
)


def candidate(key: str, value: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({key: value, "certainty": certainty, "evidence": evidence})


def completion(threat: bool, food_offer: bool):
    async def complete(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return candidate("threat", threat, 0.8, "I will hurt you" if threat else None)
        return candidate("food_offer", food_offer, 0.8, "I offer you this fresh meat" if food_offer else None)

    return complete


def test_hunger_changes_otherwise_equivalent_accepted_conflicts() -> None:
    message = "Fox, I will hurt you, but I offer you this fresh meat."

    low_hunger = asyncio.run(run_turn(message, 10, 30, completion(True, True)))
    high_hunger = asyncio.run(run_turn(message, 10, 90, completion(True, True)))

    assert low_hunger.utilities == (("flee", 60), ("approach", 30), ("do_nothing", 1))
    assert low_hunger.choice == low_hunger.executed_action == "flee"
    assert low_hunger.resulting_distance == 15
    assert low_hunger.resulting_hunger == 40
    assert high_hunger.utilities == (("flee", 60), ("approach", 90), ("do_nothing", 1))
    assert high_hunger.choice == high_hunger.executed_action == "approach"
    assert high_hunger.resulting_distance == 7
    assert high_hunger.resulting_hunger == 100


def test_safety_wins_the_fixed_tie() -> None:
    trace = asyncio.run(run_turn("Fox, I will hurt you, but I offer you this fresh meat.", 10, 60, completion(True, True)))

    assert trace.selected_utility == 60
    assert trace.selection_tie_order == ("flee", "approach", "do_nothing")
    assert trace.choice == "flee"


def test_retained_hunger_advances_once_per_valid_turn() -> None:
    case = {
        "initial_distance": 1,
        "initial_hunger": 50,
        "turns": [
            {
                "player_message": "Fox, hello.",
                "threat_completion": candidate("threat", False, 0.8, None),
                "food_offer_completion": candidate("food_offer", False, 0.8, None),
            },
            {
                "player_message": "Fox, I will hurt you, but I offer you this fresh meat.",
                "threat_completion": candidate("threat", True, 0.8, "I will hurt you"),
                "food_offer_completion": candidate("food_offer", True, 0.8, "I offer you this fresh meat"),
            },
            {
                "player_message": "Fox, I will hurt you, but I offer you this fresh meat.",
                "threat_completion": candidate("threat", True, 0.8, "I will hurt you"),
                "food_offer_completion": candidate("food_offer", True, 0.8, "I offer you this fresh meat"),
            },
        ],
    }

    traces = asyncio.run(run_fixture(case))

    assert [trace.starting_hunger for trace in traces] == [50, 60, 70]
    assert [trace.resulting_hunger for trace in traces] == [60, 70, 80]
    assert [trace.choice for trace in traces] == ["do_nothing", "flee", "approach"]
    assert [trace.resulting_distance for trace in traces] == [1, 6, 3]


@pytest.mark.parametrize("starting_hunger", [-1, 101, True, "50"])
def test_invalid_hunger_fails_before_model_calls(starting_hunger: object) -> None:
    calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return "not used"

    with pytest.raises(ValueError, match="starting_hunger"):
        asyncio.run(run_turn("Fox, hello.", 10, starting_hunger, complete))  # type: ignore[arg-type]

    assert calls == 0


def test_rejected_perceptions_contribute_no_utility_and_inaudible_turn_skips_sensors() -> None:
    rejected = asyncio.run(
        run_turn(
            "Fox, I will hurt you, but I offer you this fresh meat.",
            10,
            90,
            lambda _message, prompt: _response("not json" if "hostile threat" in prompt else "not json"),
        )
    )
    calls = 0

    async def inaudible_completion(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return "not used"

    inaudible = asyncio.run(run_turn("Fox, hello.", HEARING_RANGE + 1, 20, inaudible_completion))

    assert rejected.utilities == (("flee", 0), ("approach", 0), ("do_nothing", 1))
    assert rejected.choice == "do_nothing"
    assert rejected.threat_validation_result == rejected.food_offer_validation_result == "invalid_candidate"
    assert inaudible.heard is False
    assert inaudible.threat_sensor_called is inaudible.food_offer_sensor_called is False
    assert inaudible.utilities == (("flee", 0), ("approach", 0), ("do_nothing", 1))
    assert inaudible.resulting_hunger == 30
    assert calls == 0


async def _response(value: str) -> str:
    return value


def test_checked_in_corpus_is_reproducible_json_safe_and_has_required_cases() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_deterministic_utility.yaml"
    cases = {cast(str, case["id"]): case for case in load_corpus(corpus_path)}

    assert set(cases) == {
        "baseline",
        "single-motive",
        "low-hunger-conflict",
        "high-hunger-conflict",
        "retained-state",
        "rejected-perceptions",
    }

    first_run = {case_id: [asdict(trace) for trace in asyncio.run(run_fixture(case))] for case_id, case in cases.items()}
    second_run = {case_id: [asdict(trace) for trace in asyncio.run(run_fixture(case))] for case_id, case in cases.items()}

    assert first_run == second_run
    for case_id, case in cases.items():
        traces = first_run[case_id]
        for turn, trace in zip(cast(list[dict[str, object]], case["turns"]), traces, strict=True):
            assert trace["executed_action"] == turn["expected_action"]
            assert trace["resulting_distance"] == turn["expected_resulting_distance"]
            assert trace["resulting_hunger"] == turn["expected_resulting_hunger"]
            json.dumps(trace, sort_keys=True)
