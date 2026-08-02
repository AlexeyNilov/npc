from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

from npc.experiments import trader_offers

ROOT = Path(__file__).parents[1]
QUESTION = "Does accepting this offer fit your intent in your current situation?"


def test_later_request_receives_balance_from_earlier_accepted_offer() -> None:
    requests: list[dict[str, object]] = []

    async def completion(prompt: str, system_prompt: str) -> str:
        requests.append(json.loads(prompt))
        return json.dumps({QUESTION: True})

    result = asyncio.run(trader_offers.run(ROOT / "scenarios" / "trader_offers.yaml", completion))

    greedy_requests = [request for request in requests if request["trader"] == "greedy"]
    assert greedy_requests[1]["cash"] == 6
    assert greedy_requests[1]["inventory"] == {"apple": 3, "gem": 0}
    assert result["greedy"].cash == 13
    assert result["greedy"].inventory == {"apple": 2, "gem": 0}


def test_requests_are_limited_to_current_trader_state_offer_and_question() -> None:
    requests: list[dict[str, object]] = []

    async def completion(prompt: str, system_prompt: str) -> str:
        requests.append(json.loads(prompt))
        return json.dumps({QUESTION: False})

    asyncio.run(trader_offers.run(ROOT / "scenarios" / "trader_offers.yaml", completion))

    assert len(requests) == 6
    first = requests[0]
    assert first == {
        "trader": "greedy",
        "intent": "Build wealth by taking favorable deals.",
        "cash": 10,
        "inventory": {"apple": 2, "gem": 0},
        "offer": {
            "description": "Buy one apple for four cash.",
            "side": "buy",
            "item": "apple",
            "quantity": 1,
            "total_price": 4,
        },
        "question": QUESTION,
    }
    assert "cautious" not in json.dumps(first)
    assert "Sell one apple for seven cash." not in json.dumps(first)


def test_yaml_profile_edit_changes_request_without_changing_scenario_content(tmp_path: Path) -> None:
    scenario_content = (ROOT / "scenarios" / "trader_offers.yaml").read_text()
    greedy = yaml.safe_load((ROOT / "actors" / "trader_greedy.yaml").read_text())
    cautious = yaml.safe_load((ROOT / "actors" / "trader_cautious.yaml").read_text())
    greedy["intent"] = "Only collect maps."
    greedy["question"] = "Is this map deal worthwhile?"
    actors = tmp_path / "actors"
    scenarios = tmp_path / "scenarios"
    actors.mkdir()
    scenarios.mkdir()
    (actors / "trader_greedy.yaml").write_text(yaml.safe_dump(greedy, sort_keys=False))
    (actors / "trader_cautious.yaml").write_text(yaml.safe_dump(cautious, sort_keys=False))
    scenario_path = scenarios / "trader_offers.yaml"
    scenario_path.write_text(scenario_content)
    requests: list[dict[str, object]] = []

    async def completion(prompt: str, system_prompt: str) -> str:
        request = json.loads(prompt)
        requests.append(request)
        return json.dumps({request["question"]: False})

    asyncio.run(trader_offers.run(scenario_path, completion))

    assert requests[0]["intent"] == "Only collect maps."
    assert requests[0]["question"] == "Is this map deal worthwhile?"
    assert requests[0]["offer"] == {
        "description": "Buy one apple for four cash.",
        "side": "buy",
        "item": "apple",
        "quantity": 1,
        "total_price": 4,
    }


def test_yaml_scenario_offer_edit_changes_request_without_changing_actor_profiles(tmp_path: Path) -> None:
    scenario = yaml.safe_load((ROOT / "scenarios" / "trader_offers.yaml").read_text())
    actors = tmp_path / "actors"
    scenarios = tmp_path / "scenarios"
    actors.mkdir()
    scenarios.mkdir()
    for name in ("trader_greedy.yaml", "trader_cautious.yaml"):
        source = ROOT / "actors" / name
        destination = actors / name
        destination.write_text(source.read_text())
        assert destination.read_text() == source.read_text()
    scenario["offers"][0]["description"] = "Buy a map for four cash."
    scenario["offers"][0]["item"] = "map"
    scenario_path = scenarios / "trader_offers.yaml"
    scenario_path.write_text(yaml.safe_dump(scenario, sort_keys=False))
    requests: list[dict[str, object]] = []

    async def completion(prompt: str, system_prompt: str) -> str:
        request = json.loads(prompt)
        requests.append(request)
        return json.dumps({request["question"]: False})

    asyncio.run(trader_offers.run(scenario_path, completion))

    assert requests[0]["intent"] == "Build wealth by taking favorable deals."
    assert requests[0]["question"] == QUESTION
    assert requests[0]["offer"] == {
        "description": "Buy a map for four cash.",
        "side": "buy",
        "item": "map",
        "quantity": 1,
        "total_price": 4,
    }


@pytest.mark.parametrize("response", ["not json", '{"wrong": true}', f'{{"{QUESTION}": 1}}'])
def test_invalid_response_fails_before_proposal_or_mutation(response: str) -> None:
    balances = trader_offers.Balances(cash=10, inventory={"apple": 2})
    offer = trader_offers.Offer("Buy one apple.", "buy", "apple", 1, 4)

    async def completion(prompt: str, system_prompt: str) -> str:
        return response

    with pytest.raises(trader_offers.ResponseError):
        asyncio.run(trader_offers.evaluate_offer("greedy", "gain wealth", QUESTION, balances, offer, completion))
    assert balances == trader_offers.Balances(cash=10, inventory={"apple": 2})


@pytest.mark.parametrize(
    ("balances", "offer", "answer", "expected", "result"),
    [
        (
            trader_offers.Balances(10, {"apple": 2}),
            trader_offers.Offer("", "buy", "apple", 1, 4),
            True,
            (6, {"apple": 3}),
            "accepted",
        ),
        (
            trader_offers.Balances(3, {"apple": 2}),
            trader_offers.Offer("", "buy", "apple", 1, 4),
            True,
            (3, {"apple": 2}),
            "rejected",
        ),
        (
            trader_offers.Balances(10, {"apple": 2}),
            trader_offers.Offer("", "sell", "apple", 1, 7),
            True,
            (17, {"apple": 1}),
            "accepted",
        ),
        (
            trader_offers.Balances(10, {"apple": 0}),
            trader_offers.Offer("", "sell", "apple", 1, 7),
            True,
            (10, {"apple": 0}),
            "rejected",
        ),
        (
            trader_offers.Balances(10, {"apple": 2}),
            trader_offers.Offer("", "buy", "apple", 1, 4),
            False,
            (10, {"apple": 2}),
            "no transaction proposed",
        ),
    ],
)
def test_resolution_preserves_state_on_rejection_or_no_proposal(
    balances: trader_offers.Balances,
    offer: trader_offers.Offer,
    answer: bool,
    expected: tuple[int, dict[str, int]],
    result: str,
) -> None:
    async def completion(prompt: str, system_prompt: str) -> str:
        return json.dumps({QUESTION: answer})

    record = asyncio.run(trader_offers.evaluate_offer("greedy", "gain wealth", QUESTION, balances, offer, completion))

    assert record.result == result
    assert (balances.cash, balances.inventory) == expected


def test_cli_runs_independent_traders_and_prints_every_boundary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    requests: list[dict[str, object]] = []

    async def completion(prompt: str, system_prompt: str) -> str:
        request = json.loads(prompt)
        requests.append(request)
        return json.dumps({QUESTION: request["trader"] == "greedy"})

    monkeypatch.setattr(trader_offers, "complete_text", completion)
    monkeypatch.setattr(sys, "argv", ["trader_offers", str(ROOT / "scenarios" / "trader_offers.yaml")])

    assert trader_offers.main() == 0
    output = capsys.readouterr().out
    by_trader = {trader: [request for request in requests if request["trader"] == trader] for trader in ("greedy", "cautious")}
    expected_offers = [
        {
            "description": "Buy one apple for four cash.",
            "side": "buy",
            "item": "apple",
            "quantity": 1,
            "total_price": 4,
        },
        {
            "description": "Sell one apple for seven cash.",
            "side": "sell",
            "item": "apple",
            "quantity": 1,
            "total_price": 7,
        },
        {
            "description": "Sell one gem for five cash.",
            "side": "sell",
            "item": "gem",
            "quantity": 1,
            "total_price": 5,
        },
    ]
    assert [request["offer"] for request in by_trader["greedy"]] == expected_offers
    assert [request["offer"] for request in by_trader["cautious"]] == expected_offers
    assert by_trader["greedy"][0]["cash"] == by_trader["cautious"][0]["cash"] == 10
    assert by_trader["greedy"][0]["inventory"] == by_trader["cautious"][0]["inventory"] == {"apple": 2, "gem": 0}
    assert [request["cash"] for request in by_trader["greedy"]] == [10, 6, 13]
    assert [request["cash"] for request in by_trader["cautious"]] == [10, 10, 10]
    blocks = output.strip().split("trader: ")[1:]
    assert "cash: 13\ninventory: apple: 2, gem: 0" in blocks[2]
    assert "cash: 10\ninventory: apple: 2, gem: 0" in blocks[5]
    assert output.count("trader:") == 6
    assert output.count("intent:") == 6
    assert output.count("offer:") == 6
    assert output.count("question:") == 6
    assert output.count("answer:") == 6
    assert output.count("attempted choice:") == 6
    assert output.count("authoritative result:") == 6
    assert output.count("resulting balances:") == 6
    assert "trader: greedy" in output
    assert "trader: cautious" in output
