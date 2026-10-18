"""Compare production rankers using the same local benchmark labels."""

import json
from pathlib import Path

import httpx2
import pytest

from npc.benchmarks.action_comparison import run_comparison
from npc.benchmarks.action_ranking import BenchmarkCase
from npc.system_one import SystemOneClient

STATE = {"intent": "goal", "situation": "context"}


def test_comparison_and_label_isolation() -> None:
    """Shared rank metrics exclude unselectable cases and retain native noul scoring."""
    cases = [
        BenchmarkCase("one", STATE, ["a", "b", "c"], ["b"]),
        BenchmarkCase("two", STATE, ["d", "e", "f"], ["e", "f"]),
        BenchmarkCase("both", STATE, ["g", "h"], ["h"]),
        BenchmarkCase("neither", STATE, ["i", "j", "k"], ["k"]),
        BenchmarkCase("both_again", STATE, ["l", "m"], ["l"]),
        BenchmarkCase("neither_again", STATE, ["i", "j", "k"], ["k"]),
        BenchmarkCase("both_third", STATE, ["l", "m"], ["l"]),
        BenchmarkCase("threshold", STATE, ["harmful"], []),
        BenchmarkCase("none", STATE, ["bad"], []),
        BenchmarkCase("empty", STATE, [], []),
    ]
    requests: list[dict[str, object]] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        payload = json.loads(request.content)
        requests.append(payload)
        names = json.loads(payload["state"]["available_actions"])
        choice = "action_choice" in payload["questions"]
        scores = (
            {
                "a": 0.6,
                "b": 0.3,
                "c": 0.1,
                "d": 0.1,
                "e": 0.6,
                "f": 0.3,
                "g": 0.25,
                "h": 0.75,
                "i": 0.5,
                "j": 0.4,
                "k": 0.1,
                "l": 0.7,
                "m": 0.3,
                "bad": 1.0,
                "harmful": 1.0,
            }
            if choice
            else {
                "a": 0.2,
                "b": 0.8,
                "c": 0.1,
                "d": 0.9,
                "e": 0.2,
                "f": 0.8,
                "bad": 0.1,
                "g": 0.2,
                "h": 0.8,
                "i": 0.9,
                "j": 0.8,
                "k": 0.1,
                "l": 0.8,
                "m": 0.2,
                "harmful": 0.5,
            }
        )
        probabilities = {f"action_{i}": scores[name] for i, name in enumerate(names)}
        answers = (
            {"action_choice": {"type": "choice", "probabilities": probabilities}}
            if choice
            else {
                key: {"type": "noul", "noul": score}
                for key, score in probabilities.items()
            }
        )
        return httpx2.Response(200, json={"model": "test-model", "answers": answers})

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        report = run_comparison(
            cases,
            evaluator=SystemOneClient("http://test/rank", client=client),
            choice_evaluator=SystemOneClient("http://test/rank", client=client),
        )
    report = json.loads(json.dumps(report))
    assert len(requests) == 18
    assert all(
        isinstance(payload["state"], dict)
        and set(payload["state"]) == {"intent", "situation", "available_actions"}
        for payload in requests
    )
    assert report["noul"]["metrics"]["brier_score"] is not None
    assert report["choice"]["model"] == "test-model"
    assert "brier_score" not in report["choice"]["metrics"]
    assert report["comparison"] == {
        "paired_cases": 7,
        "noul_top1_accuracy": pytest.approx(4 / 7),
        "choice_top1_accuracy": pytest.approx(4 / 7),
        "noul_mean_reciprocal_rank": pytest.approx(31 / 42),
        "choice_mean_reciprocal_rank": pytest.approx(31 / 42),
        "noul_only_correct": 1,
        "choice_only_correct": 1,
        "both_correct": 3,
        "neither_correct": 2,
        "no_relevant_cases": 3,
        "empty_catalog_cases": 1,
        "noul_no_relevant_abstentions": 1,
        "choice_no_relevant_forced_choices": 2,
    }
    assert [row["id"] for row in report["choice"]["results"]] == [
        case.id for case in cases
    ]


@pytest.mark.parametrize("failed_approach", ["noul", "choice"])
def test_errors_are_retained_and_excluded_from_paired_scores(
    failed_approach: str,
) -> None:
    """One failed approach keeps its error and cannot bias paired scores."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        payload = json.loads(request.content)
        if ("action_choice" in payload["questions"]) == (failed_approach == "choice"):
            return httpx2.Response(503)
        if "action_choice" in payload["questions"]:
            return httpx2.Response(
                200,
                json={
                    "answers": {
                        "action_choice": {
                            "type": "choice",
                            "probabilities": {"action_0": 1.0},
                        }
                    }
                },
            )
        return httpx2.Response(
            200, json={"answers": {"action_0": {"type": "noul", "noul": 0.9}}}
        )

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        report = run_comparison(
            [BenchmarkCase("x", STATE, ["a"], ["a"])],
            evaluator=SystemOneClient("http://test/rank", client=client),
            choice_evaluator=SystemOneClient("http://test/rank", client=client),
        )
    report = json.loads(json.dumps(report))
    assert report["comparison"]["paired_cases"] == 0
    assert report["comparison"]["choice_top1_accuracy"] is None
    assert report["comparison"]["noul_mean_reciprocal_rank"] is None
    assert report[failed_approach]["metrics"]["request_error_cases"] == 1
    assert "503" in report[failed_approach]["results"][0]["error"]


def test_report_preserves_reproducible_observations() -> None:
    """Saved choice observations retain inputs, labels, probabilities, and provenance."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        questions = json.loads(request.content)["questions"]
        answers = (
            {"action_choice": {"type": "choice", "probabilities": {"action_0": 1.0}}}
            if "action_choice" in questions
            else {"action_0": {"type": "noul", "noul": 0.9}}
        )
        return httpx2.Response(200, json={"model": "test-model", "answers": answers})

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        report = json.loads(
            json.dumps(
                run_comparison(
                    [BenchmarkCase("unicode", STATE, ["réparer"], ["réparer"])],
                    evaluator=SystemOneClient("http://test/rank", client=client),
                    choice_evaluator=SystemOneClient("http://test/rank", client=client),
                )
            )
        )
    assert report["benchmark"] == "action-ranking-comparison"
    assert report["created_at"] == report["noul"]["created_at"]
    assert report["dataset_hash"] == report["noul"]["dataset_hash"]
    assert report["choice"]["prompt_version"] == "action-choice-v1"
    assert report["choice"]["elapsed_seconds"] >= 0
    row = report["choice"]["results"][0]
    assert row == {
        "id": "unicode",
        "state": STATE,
        "actions": ["réparer"],
        "relevant_actions": ["réparer"],
        "ranking": [{"action": "réparer", "probability": 1.0}],
        "error": None,
        "elapsed_seconds": row["elapsed_seconds"],
    }
    assert row["elapsed_seconds"] >= 0


def test_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparison command loads the existing dataset format and saves a report."""
    from experiments.action_ranking_comparison import main

    dataset = tmp_path / "cases.json"
    dataset.write_text(
        json.dumps(
            [{"id": "empty", "state": STATE, "actions": [], "relevant_actions": []}]
        )
    )
    monkeypatch.setenv("SYSTEM_ONE", "http://test/rank")
    output = tmp_path / "runs" / "comparison.json"
    assert main(["--input", str(dataset), "--output", str(output)]) == 0
    report = json.loads(output.read_text())
    assert report["endpoint"] == "http://test/rank"
    assert len(report["dataset_hash"]) == 64
    assert report["comparison"]["paired_cases"] == 0
