"""Benchmark comparisons, fixture loading and command-line behavior."""

import json
from pathlib import Path

import httpx2
import pytest

from npc.action_ranking import Question
from npc.benchmark import load_cases, run_benchmark
from npc.cli.benchmark import main

FIXTURE = Path("tests/fixtures/action_ranking/cases.json")


class Evaluator:
    model = "test-model"

    def __init__(self, scores: list[list[float] | None]) -> None:
        self.scores = iter(scores)
        self.states: list[dict[str, str]] = []

    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        self.states.append(state)
        scores = next(self.scores)
        if scores is None:
            raise httpx2.ConnectError("offline")
        return {
            "answers": {
                key: {"type": "noul", "noul": score}
                for key, score in zip(questions, scores, strict=True)
            }
        }


def test_fixture_labels_are_complete() -> None:
    """Every shipped case has a complete ranking and valid relevance annotations."""
    cases = load_cases(FIXTURE)
    assert len(cases) == 16
    assert len({case.id for case in cases}) == 16
    assert sum(case.pair_id is not None for case in cases) == 10
    assert cases[-1].actions == []


def test_metrics_and_no_label_leakage() -> None:
    """Scores determine ordering, ties fail strict preferences, and labels stay local."""
    cases = load_cases(FIXTURE)[:2]
    evaluator = Evaluator([[0.1, 0.2, 0.9], [0.2, 0.9, 0.9]])
    report = run_benchmark(cases, evaluator=evaluator)
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["pairwise_ordering_accuracy"] == 0.75
    assert metrics["top_action_relevance"] == 1.0
    assert metrics["comparable_cases"] == 2
    assert metrics["error_cases"] == 0
    assert report["pairs"] == [{"pair_id": "checkout_recovery", "passed": False}]
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["model"] == "test-model"
    assert results[0]["ranking"][0] == {
        "action": "read_application_logs",
        "probability": 0.9,
    }
    assert results[1]["pairwise_ordering_accuracy"] == 0.5
    assert results[0]["elapsed_seconds"] >= 0
    assert evaluator.states == [
        {"intent": case.intent, "situation": case.state} for case in cases
    ]


def test_abstention_empty_and_failures() -> None:
    """No-useful-action scores and empty catalogs remain distinct from failed requests."""
    cases = load_cases(FIXTURE)[-3:]
    evaluator = Evaluator([[0.8, 0.2, 0.1], [0.2, 0.3, 0.4]])
    report = run_benchmark(cases, evaluator=evaluator)
    results = report["results"]
    assert isinstance(results, list)
    assert [result["max_probability"] for result in results] == [0.8, 0.4, None]
    assert results[-1]["ranking"] == []
    assert results[-1]["model"] is None
    assert len(evaluator.states) == 2
    failed = run_benchmark(load_cases(FIXTURE)[:2], evaluator=FailingEvaluator())
    metrics = failed["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["error_cases"] == 2
    assert metrics["pairwise_ordering_accuracy"] is None
    assert failed["pairs"] == [{"pair_id": "checkout_recovery", "passed": False}]


class FailingEvaluator:
    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        from npc.system_one import SystemOneError

        raise SystemOneError("offline")


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_id",
        "duplicate_action",
        "missing_tier_action",
        "unknown_relevant_action",
        "blank_intent",
    ],
)
def test_invalid_fixture(tmp_path: Path, change: str) -> None:
    """Broken labels fail loading rather than producing misleading measurements."""
    data = json.loads(FIXTURE.read_text())[:2]
    if change == "duplicate_id":
        data[1]["id"] = data[0]["id"]
    elif change == "duplicate_action":
        data[0]["actions"].append(data[0]["actions"][0])
    elif change == "missing_tier_action":
        data[0]["expected_tiers"][0] = []
    elif change == "unknown_relevant_action":
        data[0]["relevant_actions"] = ["unknown"]
    else:
        data[0]["intent"] = " "
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


def test_cli_missing_configuration(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing endpoint produces an actionable error and no result JSON."""
    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    assert main(["--input", str(FIXTURE)]) == 1
    output = capsys.readouterr()
    assert "SYSTEM_ONE" in output.err
    assert output.out == ""


def test_cli_empty_catalog(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The command writes a machine-readable report without contacting the endpoint."""
    monkeypatch.setenv("SYSTEM_ONE", "http://127.0.0.1:1/v1/systemone")
    data = json.loads(FIXTURE.read_text())[-1:]
    path, output = tmp_path / "cases.json", tmp_path / "report.json"
    path.write_text(json.dumps(data))
    assert (
        main(
            [
                "--input",
                str(path),
                "--output",
                str(output),
                "--model-version",
                "fixture-model",
                "--server-version",
                "fixture-server",
            ]
        )
        == 0
    )
    report = json.loads(output.read_text())
    assert report["results"][0]["ranking"] == []
    assert report["model_version"] == "fixture-model"
    assert report["server_version"] == "fixture-server"
    assert report["endpoint"] == "http://127.0.0.1:1/v1/systemone"


def test_successful_pairs_and_false_top_action() -> None:
    """Perfect ordering passes a controlled pair; a wrong top action is measured."""
    from datetime import datetime

    from npc.action_ranking import PROMPT_VERSION

    cases = load_cases(FIXTURE)[:2]
    perfect = run_benchmark(
        cases, evaluator=Evaluator([[0.1, 0.2, 0.9], [0.1, 0.9, 0.2]])
    )
    assert perfect["pairs"] == [{"pair_id": "checkout_recovery", "passed": True}]
    assert perfect["prompt_version"] == PROMPT_VERSION
    assert isinstance(perfect["created_at"], str)
    assert datetime.fromisoformat(perfect["created_at"]).utcoffset() is not None
    wrong = run_benchmark(
        cases, evaluator=Evaluator([[0.9, 0.2, 0.1], [0.1, 0.9, 0.2]])
    )
    assert wrong["metrics"] == {
        "total_cases": 2,
        "error_cases": 0,
        "comparable_cases": 2,
        "noncomparable_successful_cases": 0,
        "pairwise_ordering_accuracy": 0.5,
        "top_action_relevance": 0.5,
        "top_action_evaluated_cases": 2,
    }


@pytest.mark.parametrize("payload", [None, {}, [None], [{"expected_tiers": None}]])
def test_invalid_fixture_shapes(tmp_path: Path, payload: object) -> None:
    """Malformed JSON structures produce fixture validation errors."""
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_cases(path)


@pytest.mark.parametrize("field", ["actions", "expected_tiers", "relevant_actions"])
def test_invalid_fixture_lists(tmp_path: Path, field: str) -> None:
    """Fixture names and tier lists must be actual lists rather than strings."""
    data = json.loads(FIXTURE.read_text())[:2]
    data[0][field] = "invalid"
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


@pytest.mark.parametrize(
    "change",
    [
        "count",
        "intent",
        "actions",
        "same_state",
        "tier_identity",
        "tier_duplicate",
        "blank_pair",
    ],
)
def test_inconsistent_pairs_and_labels(tmp_path: Path, change: str) -> None:
    """Controlled comparisons require matching inputs, changed states, and exact labels."""
    data = json.loads(FIXTURE.read_text())[:2]
    if change == "count":
        data.pop()
    elif change == "same_state":
        data[1]["state"] = data[0]["state"]
    elif change == "tier_identity":
        data[0]["expected_tiers"][0] = ["unknown"]
    elif change == "tier_duplicate":
        data[0]["expected_tiers"][0] = [data[0]["expected_tiers"][1][0]]
    elif change == "blank_pair":
        data[0]["pair_id"] = " "
    elif change == "actions":
        data[1]["actions"].reverse()
    else:
        data[1]["intent"] = "Different intent"
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


def test_case_error_continues_without_zero_scores() -> None:
    """An invalid response is reported while later cases still receive real scores."""
    report = run_benchmark(
        load_cases(FIXTURE)[:2], evaluator=Evaluator([[0.1, 0.2, 2.0], [0.1, 0.9, 0.2]])
    )
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["error"].startswith("InvalidEvaluationError: ")
    assert results[0]["ranking"] == []
    assert results[0]["max_probability"] is None
    assert results[1]["error"] is None
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["total_cases"] == 2
    assert metrics["error_cases"] == 1
    assert metrics["comparable_cases"] == 1
    assert metrics["pairwise_ordering_accuracy"] == 1.0


def test_cli_stdout_and_case_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A completed command emits only report JSON and returns 2 for failed cases."""
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/v1/systemone")

    def handle(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(503)

    real_client = httpx2.Client
    clients: list[httpx2.Client] = []

    def factory() -> httpx2.Client:
        client = real_client(transport=httpx2.MockTransport(handle))
        clients.append(client)
        return client

    monkeypatch.setattr("npc.cli.benchmark.httpx2.Client", factory)
    assert main(["--input", str(FIXTURE)]) == 2
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert captured.err == ""
    assert report["metrics"]["error_cases"] == 15
    assert report["results"][0]["error"] == "SystemOneError: System One HTTP 503"
    assert clients[0].is_closed


@pytest.mark.parametrize("timeout", ["0", "-1", "inf", "nan"])
def test_cli_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], timeout: str
) -> None:
    """Invalid timeout values are reported before evaluating any scenario."""
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/v1/systemone")
    assert main(["--input", str(FIXTURE), "--timeout", timeout]) == 1
    captured = capsys.readouterr()
    assert "timeout" in captured.err
    assert captured.out == ""


def test_cli_missing_fixture(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing input is an actionable command error rather than a traceback."""
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/v1/systemone")
    assert main(["--input", str(tmp_path / "absent.json")]) == 1
    captured = capsys.readouterr()
    assert "absent.json" in captured.err
    assert captured.out == ""
