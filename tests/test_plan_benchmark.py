"""Plan benchmark contracts through files, reports, and the HTTP boundary."""

import hashlib
import json
from pathlib import Path

import httpx2
import pytest

from npc.benchmarks import plan_ranking
from npc.cli.benchmark import main
from npc.model.evaluation import Question, State
from npc.system_one import InvalidEvaluationError, SystemOneError


class Evaluator:
    model = "test-model"

    def __init__(self) -> None:
        self.states: list[State] = []

    def evaluate(
        self, state: State, questions: dict[str, Question]
    ) -> dict[str, float]:
        self.states.append(state)
        return dict(zip(questions, [0.8, 0.4], strict=True))


def write_cases(tmp_path: Path) -> Path:
    """Write labeled alternatives whose aggregate score is hand-computable."""
    cases = [
        {
            "id": "recovery",
            "state": {"intent": "Recover", "situation": "Rollback is unavailable."},
            "plans": [" Diagnose ", "Roll back"],
            "acceptable_plans": ["Diagnose"],
        },
        {
            "id": "no_solution",
            "state": {"intent": "Recover", "situation": "Neither plan can help."},
            "plans": ["Diagnose", "Roll back"],
            "acceptable_plans": [],
        },
    ]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    return path


def test_plan_scores_inputs_and_label_isolation(tmp_path: Path) -> None:
    """Reports preserve inputs and score every plan while sending only context."""
    path = write_cases(tmp_path)
    evaluator = Evaluator()
    report = plan_ranking.run(path, evaluator=evaluator)
    assert report["benchmark"] == "plan-ranking"
    assert report["prompt_version"] == "plan-suitability-v1"
    assert report["dataset_hash"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert report["model"] == "test-model"
    assert report["metrics"] == {
        "total_cases": 2,
        "failed_cases": 1,
        "failed_plans": 1,
        "usefulness_threshold": 0.5,
        "request_error_cases": 0,
        "evaluated_plans": 4,
        "brier_score": pytest.approx(0.25),
    }
    results = report["results"]
    assert isinstance(results, list)
    assert [result["id"] for result in results] == ["recovery", "no_solution"]
    assert results[0]["plans"] == ["Diagnose", "Roll back"]
    assert results[0]["acceptable_plans"] == ["Diagnose"]
    assert results[0]["ranking"] == [
        {"plan": "Diagnose", "probability": 0.8},
        {"plan": "Roll back", "probability": 0.4},
    ]
    assert results[0]["brier_score"] == pytest.approx(0.1)
    assert results[1]["brier_score"] == pytest.approx(0.4)
    assert results[1]["failed_plans"] == ["Diagnose"]
    assert evaluator.states == [
        {**result["state"], "available_plans": '["Diagnose", "Roll back"]'}
        for result in results
    ]


@pytest.mark.parametrize(
    "error", [SystemOneError("offline"), InvalidEvaluationError("missing")]
)
def test_plan_errors_continue(tmp_path: Path, error: Exception) -> None:
    """A failed request stays unscored and does not prevent subsequent evaluation."""

    class SometimesFails(Evaluator):
        def evaluate(
            self, state: State, questions: dict[str, Question]
        ) -> dict[str, float]:
            if not self.states:
                self.states.append(state)
                raise error
            return super().evaluate(state, questions)

    report = plan_ranking.run(write_cases(tmp_path), evaluator=SometimesFails())
    results = report["results"]
    assert isinstance(results, list)
    assert results[0]["error"] == f"{type(error).__name__}: {error}"
    assert results[0]["ranking"] == []
    assert results[0]["failed_plans"] is None
    assert results[0]["brier_score"] is None
    assert results[0]["acceptable_plans"] == ["Diagnose"]
    assert results[1]["error"] is None
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["request_error_cases"] == 1
    assert metrics["evaluated_plans"] == 2
    assert metrics["brier_score"] == pytest.approx(0.4)


@pytest.mark.parametrize("change", ["labels", "duplicates", "state", "limit", "ids"])
def test_invalid_plan_cases(tmp_path: Path, change: str) -> None:
    """Invalid cases fail before any request or misleading report is produced."""
    path = write_cases(tmp_path)
    data = json.loads(path.read_text())
    if change == "labels":
        data[0]["acceptable_plans"] = ["Unknown"]
    elif change == "duplicates":
        data[0]["plans"] = ["Diagnose", " Diagnose "]
    elif change == "state":
        data[0]["state"]["available_plans"] = "[]"
    elif change == "limit":
        data[0]["plans"] = [str(i) for i in range(11)]
    else:
        data[1]["id"] = data[0]["id"]
    path.write_text(json.dumps(data))
    evaluator = Evaluator()
    with pytest.raises(ValueError):
        plan_ranking.run(path, evaluator=evaluator)
    assert evaluator.states == []


def test_plan_cli_selection_and_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI selects plans, saves metadata, and closes its HTTP client."""
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/systemone")
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        payload = json.loads(request.content)
        requests.append(request)
        return httpx2.Response(
            200,
            json={
                "model": "served-model",
                "answers": {
                    key: {"type": "noul", "noul": 0.5} for key in payload["questions"]
                },
            },
        )

    client = httpx2.Client(transport=httpx2.MockTransport(handle))
    monkeypatch.setattr("npc.cli.benchmark.httpx2.Client", lambda: client)
    output = tmp_path / "nested" / "report.json"
    assert (
        main(
            [
                "--benchmark",
                "plan-ranking",
                "--input",
                str(write_cases(tmp_path)),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    report = json.loads(output.read_text())
    assert report["benchmark"] == "plan-ranking"
    assert report["model"] == "served-model"
    assert report["results"][0]["failed_plans"] == ["Roll back"]
    assert all(
        "available_plans" in json.loads(request.content)["state"]
        for request in requests
    )
    assert client.is_closed


def test_empty_plan_catalog(tmp_path: Path) -> None:
    """An empty catalog makes no request and contributes no score."""
    path = write_cases(tmp_path)
    data = json.loads(path.read_text())[:1]
    data[0].update(plans=[], acceptable_plans=[])
    path.write_text(json.dumps(data))
    evaluator = Evaluator()
    report = plan_ranking.run(path, evaluator=evaluator)
    assert evaluator.states == []
    assert report["model"] is None
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    assert metrics["evaluated_plans"] == 0
    assert metrics["brier_score"] is None


def test_maintained_plan_dataset() -> None:
    """The maintained cases include complete alternatives, no solution, and no plans."""
    cases = plan_ranking.load_cases(Path("benchmarks/plan_ranking.json"))
    assert len(cases) == 6
    assert len({case.id for case in cases}) == 6
    assert any(case.plans and not case.acceptable_plans for case in cases)
    assert cases[-1].plans == []


def test_raw_experiment_observations() -> None:
    """Exploration retains predictions and errors without inventing correctness labels."""
    from npc.benchmarks.runner import Case, observe_cases

    cases = [
        Case(
            "baseline", {"intent": "Recover", "situation": "Healthy"}, ["Diagnose"], []
        ),
        Case(
            "changed",
            {"intent": "Recover", "situation": "Unavailable"},
            ["Diagnose"],
            [],
        ),
    ]

    def predict(case: Case) -> list[tuple[str, float]]:
        if case.id == "changed":
            raise SystemOneError("offline")
        return [("Diagnose", 0.8)]

    results, model, elapsed = observe_cases(
        cases, predict=predict, evaluator=Evaluator()
    )
    assert results[0].ranking == [("Diagnose", 0.8)]
    assert results[1].error == "SystemOneError: offline"
    assert results[1].ranking == []
    assert all(
        result.brier_score is None and result.failed is None for result in results
    )
    assert model == "test-model"
    assert elapsed >= 0


@pytest.mark.parametrize("payload", [None, {}, [None], [{}]])
def test_invalid_plan_file_shapes(tmp_path: Path, payload: object) -> None:
    """Malformed datasets produce validation errors before evaluation."""
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        plan_ranking.load_cases(path)


@pytest.mark.parametrize("value", [None, "", " ", 1])
@pytest.mark.parametrize("field", ["id", "plans", "acceptable_plans"])
def test_invalid_plan_text(tmp_path: Path, field: str, value: object) -> None:
    """Identifiers, plans, and labels require nonblank text."""
    path = write_cases(tmp_path)
    data = json.loads(path.read_text())
    data[0][field] = value if field == "id" else [value]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        plan_ranking.load_cases(path)


@pytest.mark.parametrize("field", ["plans", "acceptable_plans"])
@pytest.mark.parametrize("value", ["Diagnose", None, ["Diagnose", " Diagnose "]])
def test_invalid_plan_lists(tmp_path: Path, field: str, value: object) -> None:
    """Candidates and labels are lists with unique names after trimming."""
    path = write_cases(tmp_path)
    data = json.loads(path.read_text())
    data[0][field] = value
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        plan_ranking.load_cases(path)
