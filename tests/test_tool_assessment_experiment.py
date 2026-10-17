"""Contracts for auditable comparison with unchanged relevance ranking."""

import json
from pathlib import Path

import pytest

from npc.action_ranking import Question
from npc.system_one import SystemOneError
from npc.tool_assessment_experiment import load_cases, run_experiment

FIXTURE = Path("tests/fixtures/tool_assessment/cases.json")


class Evaluator:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        self.calls.append(state)
        return {
            "model": "test-model",
            "usage": {"input_tokens": 12},
            "answers": {
                key: {"type": "noul", "noul": 0.9 if key.endswith("ready") else 0.8}
                for key in questions
            },
        }


def test_fixture_and_split() -> None:
    """Paired states stay in one split so held-out families are unseen in tuning."""
    cases = load_cases(FIXTURE)
    assert len(cases) == 8
    families: dict[str, set[str]] = {}
    for case in cases:
        families.setdefault(case.family, set()).add(case.split)
    assert all(len(splits) == 1 for splits in families.values())
    assert {case.split for case in cases} == {"development", "held-out"}


def test_recording() -> None:
    """Reports preserve evidence and denominators while labels stay outside requests."""
    cases = load_cases(FIXTURE)[:2]
    evaluator = Evaluator()
    report = run_experiment(
        cases, evaluator=evaluator, usefulness_cutoff=0.6, readiness_cutoff=0.7
    )
    assert len(evaluator.calls) == 4
    assert all(
        set(state) <= {"intent", "situation", "available_tools"}
        for state in evaluator.calls
    )
    assert report["cutoffs"] == {"usefulness": 0.6, "readiness": 0.7}
    results = report["results"]
    assert isinstance(results, list)
    assert len(results) == 4
    first = results[0]
    assert first["strategy"] == "assessment"
    assert first["recommendation"] == cases[0].tools[0]
    assert len(first["scores"]) == 2
    assert first["request"]["state"]["situation"] == cases[0].state
    assert set(first["request"]) == {"state", "questions"}
    assert first["response"]["model"] == "test-model"
    assert first["model"] == "test-model"
    assert first["elapsed_seconds"] >= 0
    assert first["input_tokens"] == 12
    assert first["prompt_version"] == "tool-assessment-v1"
    assert results[1]["prompt_version"] == "action-relevance-v2"
    assert results[1]["scores"] == [
        {"action": name, "probability": 0.8} for name in cases[0].tools
    ]
    assert first["error"] is None
    json.dumps(report, allow_nan=False)


def test_metrics() -> None:
    """Accuracy and cost counts use explicit denominators and exclude absent judgments."""
    report = run_experiment(
        load_cases(FIXTURE)[:2],
        evaluator=Evaluator(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assessment = metrics["assessment"]
    assert assessment["correct_recommendations"] == 1
    assert assessment["successful_cases"] == 2
    assert assessment["blocked_recommendations"] == 1
    assert assessment["readiness_correct"] == 3
    assert assessment["readiness_judgments"] == 4
    assert assessment["input_tokens"] == 24
    assert assessment["model_calls"] == 2
    assert metrics["relevance"]["readiness_judgments"] == 0
    json.dumps(report, allow_nan=False)


def test_errors_remain_measurements() -> None:
    """Failed assessments retain request evidence and never count as abstentions."""

    class Broken(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            raise SystemOneError("offline")

    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Broken(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["error"] == "SystemOneError: offline"
    assert results[0]["response"] is None
    assert results[0]["scores"] == []
    assert results[0]["request"] is not None
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["assessment"]["error_cases"] == 1
    assert metrics["assessment"]["successful_cases"] == 0
    assert metrics["assessment"]["abstentions"] == 0


def test_empty_catalog() -> None:
    """Empty catalogs have correct abstention without fabricated model calls or cost."""
    from dataclasses import replace

    case = replace(
        load_cases(FIXTURE)[0],
        tools=(),
        expected=(None,),
        ready_tools=(),
        preparation_tools=(),
    )
    evaluator = Evaluator()
    report = run_experiment(
        [case], evaluator=evaluator, usefulness_cutoff=0.6, readiness_cutoff=0.7
    )
    assert evaluator.calls == []
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    for strategy in ("assessment", "relevance"):
        assert metrics[strategy]["abstentions"] == 1
        assert metrics[strategy]["correct_recommendations"] == 1
        assert metrics[strategy]["model_calls"] == 0


@pytest.mark.parametrize(
    "change",
    [
        {"expected": ["nonexistent"]},
        {"ready_tools": ["nonexistent"]},
        {"preparation_tools": ["nonexistent"]},
        {"tools": ["a", "a"]},
        {"split": "test"},
        {"state": ""},
        {"expected": []},
    ],
)
def test_bad_fixture(tmp_path: Path, change: dict[str, object]) -> None:
    """Invalid annotations fail locally before any experiment can consume calls."""
    rows = json.loads(FIXTURE.read_text())
    rows[0].update(change)
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        load_cases(path)


def test_family_leakage(tmp_path: Path) -> None:
    """Splitting a scenario pair across tuning and evaluation is rejected."""
    rows = json.loads(FIXTURE.read_text())
    rows[1]["split"] = "held-out"
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="family"):
        load_cases(path)


@pytest.mark.parametrize(
    "payload", [None, {"answers": {}}, {"model": "bad", "answers": []}]
)
def test_malformed_model_response(payload: object) -> None:
    """Malformed responses are retained for diagnosis and counted as errors."""

    class Malformed(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            return payload

    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Malformed(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["response"] == payload
    assert results[0]["error"].startswith("InvalidEvaluationError:")
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["assessment"]["model_calls"] == 1
    assert metrics["assessment"]["calls_with_reported_tokens"] == 0


def test_preparation_metric() -> None:
    """Choosing already completed preparation is reported separately from readiness."""

    class Prepare(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            return {
                "answers": {
                    key: {
                        "type": "noul",
                        "noul": 1 if key.startswith(("tool_1", "action_1")) else 0,
                    }
                    for key in questions
                }
            }

    report = run_experiment(
        load_cases(FIXTURE)[1:2],
        evaluator=Prepare(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    for strategy in ("assessment", "relevance"):
        assert metrics[strategy]["unnecessary_preparation"] == 1
        assert metrics[strategy]["blocked_recommendations"] == 0
        assert metrics[strategy]["correct_recommendations"] == 0


@pytest.mark.parametrize("cutoff", [-0.1, float("nan")])
def test_invalid_configuration(cutoff: float) -> None:
    """Invalid experiment cutoffs fail before model calls even with no cases."""
    evaluator = Evaluator()
    with pytest.raises(ValueError):
        run_experiment(
            [], evaluator=evaluator, usefulness_cutoff=cutoff, readiness_cutoff=0.7
        )
    assert evaluator.calls == []


@pytest.mark.parametrize("status", [200, 503])
@pytest.mark.parametrize("split", ["development", "held-out"])
@pytest.mark.parametrize("timeout", [None, "7.5"])
def test_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    split: str,
    timeout: str | None,
) -> None:
    """The command selects one split, saves errors, and closes its HTTP client."""
    import httpx2

    from npc.tool_assessment_experiment import main

    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        questions = json.loads(request.content)["questions"]
        return httpx2.Response(
            status,
            json={"answers": {key: {"type": "noul", "noul": 0.8} for key in questions}},
        )

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    monkeypatch.setattr("npc.tool_assessment_experiment.httpx2.Client", lambda: client)
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/v1/systemone")
    output = tmp_path / "report.json"
    code = main(
        [
            "--input",
            str(FIXTURE),
            "--split",
            split,
            "--usefulness-cutoff",
            "0.6",
            "--readiness-cutoff",
            "0.7",
            "--output",
            str(output),
        ]
        + ([] if timeout is None else ["--timeout", timeout])
    )
    assert code == (0 if status == 200 else 2)
    assert client.is_closed
    assert len(requests) == 8
    report = json.loads(output.read_text())
    expected_timeout = 30.0 if timeout is None else float(timeout)
    assert requests[0].extensions["timeout"]["read"] == expected_timeout
    assert report["timeout_seconds"] == expected_timeout
    assert report["endpoint"] == "http://example.test/v1/systemone"
    assert report["split"] == split
    assert all(row["case"]["split"] == split for row in report["results"])
    assert report["metrics"]["assessment"]["error_cases"] == (0 if status == 200 else 4)


def test_command_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing endpoint configuration returns a local error without writing a report."""
    from npc.tool_assessment_experiment import main

    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    output = tmp_path / "report.json"
    assert (
        main(
            [
                "--input",
                str(FIXTURE),
                "--split",
                "development",
                "--usefulness-cutoff",
                "0.6",
                "--readiness-cutoff",
                "0.7",
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert not output.exists()
    assert "SYSTEM_ONE" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("metadata", "model", "tokens"),
    [
        ({"model": 123, "usage": {"input_tokens": True}}, None, None),
        ({"model": "m", "usage": {"input_tokens": 0}}, "m", 0),
        ({"usage": {"input_tokens": -1}}, None, None),
        ({"usage": {"input_tokens": "12"}}, None, None),
        ({"usage": []}, None, None),
    ],
)
def test_metadata(
    metadata: dict[str, object], model: str | None, tokens: int | None
) -> None:
    """Unknown or invalid metadata stays unknown while valid zero usage is retained."""

    class Metadata(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            return {
                **metadata,
                "answers": {key: {"type": "noul", "noul": 0.8} for key in questions},
            }

    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Metadata(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    results = report["results"]
    assert isinstance(results, list)
    assert all(r["model"] == model and r["input_tokens"] == tokens for r in results)
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["assessment"]["calls_with_reported_tokens"] == int(
        tokens is not None
    )


def test_elapsed_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """Recorded latency is elapsed duration and totals include both attempted calls."""
    from datetime import datetime, timedelta

    ticks = iter([10.0, 11.0, 20.0, 22.0])
    monkeypatch.setattr(
        "npc.tool_assessment_experiment.perf_counter", lambda: next(ticks)
    )
    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Evaluator(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    results = report["results"]
    assert isinstance(results, list)
    assert [r["elapsed_seconds"] for r in results] == [1.0, 2.0]
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["assessment"]["elapsed_seconds"] == 1.0
    assert metrics["relevance"]["elapsed_seconds"] == 2.0
    assert isinstance(report["created_at"], str)
    assert datetime.fromisoformat(report["created_at"]).utcoffset() == timedelta(0)


def test_readiness_boundary_and_needed_preparation() -> None:
    """Readiness metrics use the same inclusive cutoff as selection; needed prep is useful."""

    class Prepare(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            return {
                "answers": {
                    key: {
                        "type": "noul",
                        "noul": 0.7 if key.startswith(("tool_1", "action_1")) else 0.1,
                    }
                    for key in questions
                }
            }

    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Prepare(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["assessment"]["readiness_correct"] == 2
    assert metrics["assessment"]["unnecessary_preparation"] == 0
    assert metrics["assessment"]["correct_recommendations"] == 1


def test_complete_labels(tmp_path: Path) -> None:
    """All available tools may be labeled ready even when none is useful enough."""
    rows = json.loads(FIXTURE.read_text())
    rows[0].update(expected=[None], ready_tools=rows[0]["tools"])
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(rows))
    assert load_cases(path)[0].expected == (None,)


@pytest.mark.parametrize(
    "option",
    ["--input", "--split", "--output", "--usefulness-cutoff", "--readiness-cutoff"],
)
def test_required_options(option: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Missing required options produce argparse usage errors before any model call."""
    from npc.tool_assessment_experiment import main

    values = {
        "--input": str(FIXTURE),
        "--split": "development",
        "--output": "/tmp/unused.json",
        "--usefulness-cutoff": "0.6",
        "--readiness-cutoff": "0.7",
    }
    args = [
        part for key, value in values.items() if key != option for part in (key, value)
    ]
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert option in capsys.readouterr().err


def test_unknown_split(capsys: pytest.CaptureFixture[str]) -> None:
    """The command rejects unknown split names rather than evaluating an empty set."""
    from npc.tool_assessment_experiment import main

    with pytest.raises(SystemExit) as error:
        main(
            [
                "--input",
                str(FIXTURE),
                "--split",
                "unknown",
                "--output",
                "/tmp/unused.json",
                "--usefulness-cutoff",
                "0.6",
                "--readiness-cutoff",
                "0.7",
            ]
        )
    assert error.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_response_report(value: float) -> None:
    """Invalid nonfinite model scores remain inspectable in a strict JSON error report."""

    class Nonfinite(Evaluator):
        def evaluate(
            self, state: dict[str, str], questions: dict[str, Question]
        ) -> object:
            return {
                "answers": {key: {"type": "noul", "noul": value} for key in questions}
            }

    report = run_experiment(
        load_cases(FIXTURE)[:1],
        evaluator=Nonfinite(),
        usefulness_cutoff=0.6,
        readiness_cutoff=0.7,
    )
    json.dumps(report, allow_nan=False)
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["error"].startswith("InvalidEvaluationError:")
    raw = json.loads(results[0]["response"]["nonfinite_response"])
    assert set(raw["answers"]) == set(results[0]["request"]["questions"])
