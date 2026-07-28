from __future__ import annotations

import asyncio
import sys
from dataclasses import fields
from pathlib import Path
from subprocess import run

import pytest
import yaml  # type: ignore[import-untyped]

from npc import __main__
from npc.simulation import PerceptionConfig, Proposal, State, load_scenario, perceive, resolve, select_proposal

ROOT = Path(__file__).parents[1]


def test_actor_profiles_declare_binary_perception_questions() -> None:
    for name in ("beast.yaml", "beast_food_first.yaml", "beast_unsupported.yaml"):
        assert "perception_questions: []" in (ROOT / "actors" / name).read_text()


def test_perception_request_contains_all_questions_and_only_accessible_world_data(monkeypatch: pytest.MonkeyPatch) -> None:
    state, _, perception = load_scenario(ROOT / "scenarios" / "beast_perception.yaml")
    requests: list[tuple[str, str]] = []

    async def mocked_completion(prompt: str, system_prompt: str) -> str:
        requests.append((prompt, system_prompt))
        return '{"Is the wolf dangerous?": true, "Is food available?": false}'

    monkeypatch.setattr("npc.simulation.complete_text", mocked_completion)

    assert asyncio.run(perceive(state, perception)) == {
        "Is the wolf dangerous?": True,
        "Is food available?": False,
    }
    assert len(requests) == 1
    prompt, system_prompt = requests[0]
    assert "Is the wolf dangerous?" in prompt
    assert "Is food available?" in prompt
    assert "wolf" in prompt
    assert "berry" in prompt
    assert "hidden_cache" not in prompt
    for forbidden in ("move", "consume", "flee", "proposal", "destination", "target", "rule", "accepted", "rejected"):
        assert forbidden not in prompt.lower()
    assert "JSON object" in system_prompt
    assert {field.name for field in fields(State)} == {"actor_id", "actor_location", "capabilities", "entities"}
    assert isinstance(perception, PerceptionConfig)


def test_perception_accepts_a_standalone_json_code_fence(monkeypatch: pytest.MonkeyPatch) -> None:
    state, _, perception = load_scenario(ROOT / "scenarios" / "beast_perception.yaml")

    async def mocked_completion(prompt: str, system_prompt: str) -> str:
        return '```json\n{"Is the wolf dangerous?": true, "Is food available?": false}\n```'

    monkeypatch.setattr("npc.simulation.complete_text", mocked_completion)

    assert asyncio.run(perceive(state, perception)) == {
        "Is the wolf dangerous?": True,
        "Is food available?": False,
    }


def test_perception_answer_selects_profile_rule_and_yaml_question_change_alters_selection(
    tmp_path: Path,
) -> None:
    state, rules, _ = load_scenario(ROOT / "scenarios" / "beast_perception.yaml")

    flee = select_proposal(state, rules, {"Is the wolf dangerous?": True, "Is food available?": False})
    food = select_proposal(state, rules, {"Is the wolf dangerous?": False, "Is food available?": True})
    assert flee is not None
    assert food is not None
    assert flee.label == "flee"
    assert food.label == "move toward food"

    changed_profile = yaml.safe_load((ROOT / "actors" / "beast_perception.yaml").read_text())
    changed_profile["rules"][0]["when"]["perception_answer"]["is"] = False
    changed_path = tmp_path / "beast_perception_changed.yaml"
    changed_path.write_text(yaml.safe_dump(changed_profile, sort_keys=False))
    changed_scenario = tmp_path / "changed_scenario.yaml"
    changed_scenario.write_text(
        (ROOT / "scenarios" / "beast_perception.yaml")
        .read_text()
        .replace("../actors/beast_perception.yaml", "beast_perception_changed.yaml")
    )
    changed_state, changed_rules, _ = load_scenario(changed_scenario)
    changed = select_proposal(changed_state, changed_rules, {"Is the wolf dangerous?": False, "Is food available?": False})
    assert changed is not None
    assert changed.label == "flee"


@pytest.mark.parametrize(
    ("completion", "reason"),
    [
        ("not json", "malformed"),
        ('{"Is the wolf dangerous?": true}', "exactly"),
        ('{"Is the wolf dangerous?": true, "Is food available?": false, "extra": true}', "exactly"),
        ('{"Is the wolf dangerous?": 1, "Is food available?": false}', "boolean"),
    ],
)
def test_invalid_perception_response_stops_before_selection_or_resolution(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], completion: str, reason: str
) -> None:
    async def mocked_completion(prompt: str, system_prompt: str) -> str:
        return completion

    monkeypatch.setattr("npc.simulation.complete_text", mocked_completion)
    monkeypatch.setattr(__main__, "select_proposal", lambda *args: pytest.fail("selection must not run"))
    monkeypatch.setattr(__main__, "resolve", lambda *args: pytest.fail("resolution must not run"))
    monkeypatch.setattr(sys, "argv", ["npc", str(ROOT / "scenarios" / "beast_perception.yaml")])

    assert __main__.main() == 1
    diagnostic = capsys.readouterr().err
    assert reason in diagnostic
    if completion == "not json":
        assert repr(completion) in diagnostic


def test_unavailable_perception_is_a_diagnostic_cli_failure_before_selection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def unavailable(prompt: str, system_prompt: str) -> str:
        raise RuntimeError("offline")

    monkeypatch.setattr("npc.simulation.complete_text", unavailable)
    monkeypatch.setattr(__main__, "select_proposal", lambda *args: pytest.fail("selection must not run"))
    monkeypatch.setattr(sys, "argv", ["npc", str(ROOT / "scenarios" / "beast_perception.yaml")])

    assert __main__.main() == 1
    assert "perception error" in capsys.readouterr().err


def test_perception_informed_unsupported_proposal_reaches_existing_resolver() -> None:
    state, rules, _ = load_scenario(ROOT / "scenarios" / "beast_perception.yaml")

    proposal = select_proposal(state, rules, {"Is the wolf dangerous?": False, "Is food available?": False})
    assert proposal is not None
    outcome = resolve(state, proposal)

    assert outcome.narration == "rejected wait: unsupported action 'wait'"
    assert state.actor_location == 0


def run_scenario(name: str) -> list[str]:
    completed = run(
        [sys.executable, "-m", "npc", str(ROOT / "scenarios" / name)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.splitlines()


def test_command_line_narrates_flee_then_food_then_eating() -> None:
    assert run_scenario("beast.yaml") == [
        "accepted flee: beast moved from 0 to -1",
        "accepted move toward food: beast moved from -1 to -2",
        "accepted move toward food: beast moved from -2 to -3",
        "accepted eat: beast consumed berry",
    ]


def test_eating_before_colocation_is_rejected_without_state_change() -> None:
    state, _, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")

    outcome = resolve(state, Proposal("consume", "beast", target="berry", label="eat"))

    assert outcome.narration == "rejected eat: actor and target are not co-located"
    assert state.actor_location == 0
    assert state.entities["berry"].consumed is False


def test_profile_declared_capability_gates_consumption() -> None:
    state, _, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")
    state.actor_location = state.entities["berry"].location
    state.capabilities.remove("consume")

    outcome = resolve(state, Proposal("consume", "beast", target="berry", label="eat"))

    assert outcome.narration == "rejected eat: consumption is not permitted"
    assert state.entities["berry"].consumed is False


def test_unsupported_proposal_is_rejected_and_narrated_without_transition() -> None:
    state, _, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")

    outcome = resolve(state, Proposal("dance", "beast", label="dance"))

    assert outcome.narration == "rejected dance: unsupported action 'dance'"
    assert state.actor_location == 0
    assert state.entities["berry"].consumed is False


def test_command_line_can_show_an_unsupported_proposal_rejection() -> None:
    assert run_scenario("unsupported.yaml") == ["rejected dance: unsupported action 'dance'"]


def test_yaml_rule_order_changes_selected_proposal_when_food_and_threat_coexist() -> None:
    threat_first = yaml.safe_load((ROOT / "actors" / "beast.yaml").read_text())
    food_first = yaml.safe_load((ROOT / "actors" / "beast_food_first.yaml").read_text())

    assert threat_first["rules"] != food_first["rules"]
    assert sorted(threat_first["rules"], key=repr) == sorted(food_first["rules"], key=repr)
    assert run_scenario("conflict_threat_first.yaml")[0] == "accepted flee: beast moved from 0 to -1"
    assert run_scenario("conflict_food_first.yaml")[0] == "accepted eat: beast consumed berry"


def test_two_scenarios_reuse_one_profile_and_change_trace_with_content_only() -> None:
    normal = run_scenario("beast.yaml")
    changed = run_scenario("beast_food_nearby.yaml")

    assert normal != changed
    assert "actor_profile: ../actors/beast.yaml" in (ROOT / "scenarios" / "beast.yaml").read_text()
    assert "actor_profile: ../actors/beast.yaml" in (ROOT / "scenarios" / "beast_food_nearby.yaml").read_text()


def test_core_has_no_beast_specific_policy() -> None:
    core_source = (ROOT / "src" / "npc" / "simulation.py").read_text().lower()

    assert "beast" not in core_source
    assert "threat" not in core_source
    assert "food" not in core_source
