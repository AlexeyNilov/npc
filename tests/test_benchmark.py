"""Usefulness probabilities, fixture loading and command-line behavior."""

import json
from pathlib import Path

import httpx2
import pytest

from npc.benchmark import load_cases, run_benchmark
from npc.cli.benchmark import main
from npc.model.evaluation import Question, State
from npc.system_one import InvalidEvaluationError

FIXTURE = Path("tests/fixtures/action_ranking/cases.json")


class Evaluator:
    model = "test-model"

    def __init__(self, scores: list[list[float] | None]) -> None:
        self.scores = iter(scores)
        self.states: list[State] = []

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        self.states.append(state)
        scores = next(self.scores)
        if scores is None:
            raise httpx2.ConnectError("offline")
        return dict(zip(questions, scores, strict=True))


def test_fixture_labels_are_complete() -> None:
    """Every shipped scenario loads with valid usefulness annotations."""
    cases = load_cases(FIXTURE)
    assert len(cases) == 60
    assert len({case.id for case in cases}) == 60
    assert cases[-1].actions == []


@pytest.mark.parametrize("name", ["laya", None, 123])
def test_report_model(name: object) -> None:
    """The served model appears once at run level when its name is available."""
    evaluator = Evaluator([[0.1, 0.2, 0.9], [0.2, 0.9, 0.9]])
    object.__setattr__(evaluator, "model", name)
    report = run_benchmark(load_cases(FIXTURE)[:2], evaluator=evaluator)
    assert report["model"] == (name if isinstance(name, str) else None)
    assert "models" not in report
    results = report["results"]
    assert isinstance(results, list)
    assert all("model" not in result for result in results)
    assert run_benchmark([], evaluator=Evaluator([]))["model"] is None
    assert (
        run_benchmark(load_cases(FIXTURE)[-1:], evaluator=Evaluator([]))["model"]
        is None
    )


def test_metrics_and_no_label_leakage() -> None:
    """Every probability is scored against usefulness; labels stay local."""
    cases = load_cases(FIXTURE)[:2]
    evaluator = Evaluator([[0.1, 0.2, 0.9], [0.2, 0.9, 0.9]])
    report = run_benchmark(cases, evaluator=evaluator)
    assert report["model"] == "test-model"
    assert report["metrics"] == {
        "total_cases": 2,
        "failed_cases": 1,
        "failed_actions": 1,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_actions": 6,
        "brier_score": pytest.approx(0.92 / 6),
    }
    results = report["results"]
    assert isinstance(results, list)
    assert "model" not in results[0]
    assert results[0]["ranking"][0] == {
        "action": "read_application_logs",
        "probability": 0.9,
    }
    assert results[0]["relevant_actions"] == ["read_application_logs"]
    assert results[0]["brier_score"] == pytest.approx(0.02)
    assert results[1]["brier_score"] == pytest.approx(0.86 / 3)
    assert results[0]["failed_actions"] == []
    assert results[1]["failed_actions"] == ["read_application_logs"]
    assert results[0]["elapsed_seconds"] >= 0
    assert evaluator.states == [
        {
            **case.state,
            "available_actions": json.dumps(case.actions),
        }
        for case in cases
    ]


def test_no_useful_actions_empty_and_failures() -> None:
    """All-negative cases count; empty catalogs and errors invent no probabilities."""
    cases = [
        case
        for case in load_cases(FIXTURE)
        if case.id in {"invoice_already_sent", "catalog_cannot_help", "empty_catalog"}
    ]
    evaluator = Evaluator([[0.8, 0.2, 0.1], [0.2, 0.3, 0.4]])
    report = run_benchmark(cases, evaluator=evaluator)
    results = report["results"]
    assert isinstance(results, list)
    assert [result["brier_score"] for result in results] == [
        pytest.approx(0.69 / 3),
        pytest.approx(0.29 / 3),
        None,
    ]
    assert report["metrics"] == {
        "total_cases": 3,
        "failed_cases": 1,
        "failed_actions": 1,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_actions": 6,
        "brier_score": pytest.approx(0.98 / 6),
    }
    assert results[-1]["ranking"] == []
    assert results[-1]["failed_actions"] == []
    assert "model" not in results[-1]
    assert report["model"] == "test-model"
    assert len(evaluator.states) == 2
    failed = run_benchmark(load_cases(FIXTURE)[:2], evaluator=FailingEvaluator())
    assert failed["metrics"] == {
        "total_cases": 2,
        "failed_cases": 0,
        "failed_actions": 0,
        "usefulness_threshold": 0.5,
        "request_error_cases": 2,
        "evaluated_actions": 0,
        "brier_score": None,
    }


def test_useful_alternatives_need_no_preference_order() -> None:
    """Both useful delivery methods can score equally well despite different costs."""
    cases = [case for case in load_cases(FIXTURE) if case.id == "report_delivery_cost"]
    report = run_benchmark(cases, evaluator=Evaluator([[1.0, 1.0]]))
    assert report["metrics"] == {
        "total_cases": 1,
        "failed_cases": 0,
        "failed_actions": 0,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_actions": 2,
        "brier_score": 0.0,
    }


def test_action_weighted_score_and_uncertainty() -> None:
    """Each action has equal weight, including a singleton and uncertain predictions."""
    from dataclasses import replace

    base = load_cases(FIXTURE)[0]
    cases = [
        replace(base, actions=["help"], relevant_actions=["help"]),
        replace(base, actions=["a", "b", "c"], relevant_actions=[]),
    ]
    report = run_benchmark(cases, evaluator=Evaluator([[0.0], [0.5, 0.5, 0.5]]))
    assert report["metrics"] == {
        "total_cases": 2,
        "failed_cases": 2,
        "failed_actions": 4,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_actions": 4,
        "brier_score": pytest.approx(1.75 / 4),
    }


class FailingEvaluator:
    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        from npc.system_one import SystemOneError

        raise SystemOneError("offline")


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_id",
        "duplicate_action",
        "missing_relevance_labels",
        "duplicate_relevant_action",
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
    elif change == "missing_relevance_labels":
        del data[0]["relevant_actions"]
    elif change == "duplicate_relevant_action":
        data[0]["relevant_actions"] *= 2
    elif change == "unknown_relevant_action":
        data[0]["relevant_actions"] = ["unknown"]
    else:
        data[0]["state"]["intent"] = " "
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


def test_extended_fixture_state_reaches_evaluation(tmp_path: Path) -> None:
    """Benchmark loading preserves added context while keeping labels local."""
    data = json.loads(FIXTURE.read_text())[:1]
    data[0]["state"]["recent_events"] = "A release just completed."
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    cases = load_cases(path)
    evaluator = Evaluator([[0.1, 0.2, 0.9]])
    run_benchmark(cases, evaluator=evaluator)
    assert evaluator.states == [
        {**data[0]["state"], "available_actions": json.dumps(data[0]["actions"])}
    ]
    assert cases[0].state == data[0]["state"]


@pytest.mark.parametrize(
    "state",
    [
        {"intent": "goal", "situation": "circumstances", "available_actions": "[]"},
        {"intent": "goal", "situation": "circumstances", "extra": 1},
        {"intent": "goal"},
        "old situation input",
    ],
)
def test_invalid_fixture_state(tmp_path: Path, state: object) -> None:
    """Malformed or conflicting state fails at loading before benchmark execution."""
    data = json.loads(FIXTURE.read_text())[:1]
    data[0]["state"] = state
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
    assert report["timeout_seconds"] == 30.0
    assert report["server_version"] == "fixture-server"
    assert report["endpoint"] == "http://127.0.0.1:1/v1/systemone"


def test_report_metadata() -> None:
    """Reports identify the prompt and use an unambiguous timestamp."""
    from datetime import datetime

    from npc.action_ranking import PROMPT_VERSION

    report = run_benchmark([], evaluator=Evaluator([]))
    assert report["prompt_version"] == PROMPT_VERSION
    assert isinstance(report["created_at"], str)
    assert datetime.fromisoformat(report["created_at"]).utcoffset() is not None
    assert report["metrics"] == {
        "total_cases": 0,
        "failed_cases": 0,
        "failed_actions": 0,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_actions": 0,
        "brier_score": None,
    }


@pytest.mark.parametrize("payload", [None, {}, [None], [{}]])
def test_invalid_fixture_shapes(tmp_path: Path, payload: object) -> None:
    """Malformed JSON structures produce fixture validation errors."""
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_cases(path)


@pytest.mark.parametrize("field", ["actions", "relevant_actions"])
def test_invalid_fixture_lists(tmp_path: Path, field: str) -> None:
    """Action names and usefulness labels must be lists rather than strings."""
    data = json.loads(FIXTURE.read_text())[:2]
    data[0][field] = "invalid"
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


def test_case_error_continues_without_zero_scores() -> None:
    """An invalid response is reported while later cases still receive real scores."""

    class MissingAnswer(Evaluator):
        def evaluate(
            self, state: State, questions: dict[str, Question]
        ) -> dict[str, float]:
            payload = super().evaluate(state, questions)
            if len(self.states) == 1:
                raise InvalidEvaluationError("Missing answers")
            return payload

    report = run_benchmark(
        load_cases(FIXTURE)[:2],
        evaluator=MissingAnswer([[0.1, 0.2, 0.9], [0.1, 0.9, 0.2]]),
    )
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["error"].startswith("InvalidEvaluationError: ")
    assert results[0]["ranking"] == []
    assert results[0]["relevant_actions"] == ["read_application_logs"]
    assert results[0]["brier_score"] is None
    assert results[0]["failed_actions"] is None
    assert results[1]["error"] is None
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["total_cases"] == 2
    assert metrics["request_error_cases"] == 1
    assert metrics["evaluated_actions"] == 3
    assert metrics["brier_score"] == pytest.approx(0.02)


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
    assert report["metrics"]["request_error_cases"] == 59
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


def test_elapsed_time_ids_and_optional_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Case IDs survive errors, durations use differences, and model metadata is optional."""

    class NoMetadata:
        def evaluate(
            self, state: State, questions: dict[str, Question]
        ) -> dict[str, float]:
            return {key: 0.5 for key in questions}

    clock = iter(
        [9.0, 10.0, 10.25, 20.0, 20.5, 22.0, 29.0, 30.0, 30.75, 40.0, 41.0, 43.0]
    )
    monkeypatch.setattr("npc.benchmark.perf_counter", lambda: next(clock))
    cases = load_cases(FIXTURE)[:2]
    success = run_benchmark(cases, evaluator=NoMetadata())
    failure = run_benchmark(cases, evaluator=FailingEvaluator())
    assert success["elapsed_seconds"] == 13.0
    assert failure["elapsed_seconds"] == 14.0
    results = success["results"]
    assert isinstance(results, list)
    assert [(result["id"], result["elapsed_seconds"]) for result in results] == [
        (cases[0].id, 0.25),
        (cases[1].id, 0.5),
    ]
    failed = failure["results"]
    assert isinstance(failed, list)
    assert [(result["id"], result["elapsed_seconds"]) for result in failed] == [
        (cases[0].id, 0.75),
        (cases[1].id, 1.0),
    ]


def test_cli_requires_input(capsys: pytest.CaptureFixture[str]) -> None:
    """The input fixture is required by argparse before command execution."""
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2
    assert "--input" in capsys.readouterr().err


@pytest.mark.parametrize("field", ["id", "intent", "state"])
def test_standalone_blank_text(tmp_path: Path, field: str) -> None:
    """Cases reject blank identifiers and context before evaluation."""
    data = json.loads(FIXTURE.read_text())[-2:-1]
    if field == "intent":
        data[0]["state"][field] = " "
    else:
        data[0][field] = " "
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_cases(path)


def test_error_counts_and_invalid_metadata() -> None:
    """Failed cases contribute no predictions; model metadata must be text."""
    cases = load_cases(FIXTURE)[:2]
    failed = run_benchmark(cases, evaluator=FailingEvaluator())
    metrics = failed["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["evaluated_actions"] == 0
    evaluator = Evaluator([[0.1, 0.2, 0.9], [0.1, 0.9, 0.2]])
    object.__setattr__(evaluator, "model", 123)
    results = run_benchmark(cases, evaluator=evaluator)["results"]
    assert isinstance(results, list)
    assert all("model" not in result for result in results)


@pytest.mark.parametrize("probability", [0.499999, 0.5, 0.500001])
@pytest.mark.parametrize("useful", [False, True])
def test_prediction_failure_boundary(probability: float, useful: bool) -> None:
    """A score at least 0.5 predicts useful; failures identify both kinds of mistake."""
    from dataclasses import replace

    case = replace(
        load_cases(FIXTURE)[0],
        actions=["act"],
        relevant_actions=["act"] if useful else [],
    )
    report = run_benchmark([case], evaluator=Evaluator([[probability]]))
    failed = (probability >= 0.5) != useful
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["failed_actions"] == (["act"] if failed else [])
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["failed_cases"] == int(failed)
    assert metrics["failed_actions"] == int(failed)
    assert metrics["request_error_cases"] == 0
