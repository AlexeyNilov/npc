from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run

import yaml  # type: ignore[import-untyped]

from npc.simulation import Proposal, load_scenario, resolve

ROOT = Path(__file__).parents[1]


def test_actor_profiles_declare_binary_perception_questions() -> None:
    for name in ("beast.yaml", "beast_food_first.yaml", "beast_unsupported.yaml"):
        assert "perception_questions: []" in (ROOT / "actors" / name).read_text()


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
    state, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")

    outcome = resolve(state, Proposal("consume", "beast", target="berry", label="eat"))

    assert outcome.narration == "rejected eat: actor and target are not co-located"
    assert state.actor_location == 0
    assert state.entities["berry"].consumed is False


def test_profile_declared_capability_gates_consumption() -> None:
    state, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")
    state.actor_location = state.entities["berry"].location
    state.capabilities.remove("consume")

    outcome = resolve(state, Proposal("consume", "beast", target="berry", label="eat"))

    assert outcome.narration == "rejected eat: consumption is not permitted"
    assert state.entities["berry"].consumed is False


def test_unsupported_proposal_is_rejected_and_narrated_without_transition() -> None:
    state, _ = load_scenario(ROOT / "scenarios" / "beast.yaml")

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
