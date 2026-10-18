"""The maintained sensitivity experiment preserves controlled inputs and raw deltas."""

import json
from pathlib import Path

import httpx2
import pytest

from experiments.plan_context_sensitivity import main


@pytest.mark.parametrize("baseline_fails", [False, True])
def test_context_experiment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, baseline_fails: bool
) -> None:
    """Four one-fact variants share plans; deltas need a successful baseline."""
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/systemone")
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if baseline_fails and len(requests) == 1:
            return httpx2.Response(503)
        payload = json.loads(request.content)
        score = 0.8 if len(requests) == 1 else 0.3
        return httpx2.Response(
            200,
            json={
                "model": "served-model",
                "answers": {
                    key: {"type": "noul", "noul": score} for key in payload["questions"]
                },
            },
        )

    client = httpx2.Client(transport=httpx2.MockTransport(handle))
    monkeypatch.setattr(
        "experiments.plan_context_sensitivity.httpx2.Client", lambda: client
    )
    output = tmp_path / "runs" / "sensitivity.json"
    assert main(["--output", str(output)]) == (2 if baseline_fails else 0)
    report = json.loads(output.read_text())
    assert report["model"] == "served-model"
    results = report["results"]
    assert [result["id"] for result in results] == [
        "baseline",
        "incompatible_database",
        "failures_predate_release",
        "known_unrelated_cause",
    ]
    baseline = results[0]
    assert all(result["plans"] == baseline["plans"] for result in results)
    assert all(
        result["state"]["intent"] == baseline["state"]["intent"] for result in results
    )
    assert results[1]["state"]["situation"] == baseline["state"]["situation"].replace(
        "is compatible", "is incompatible"
    )
    assert results[2]["state"]["situation"] == baseline["state"]["situation"].replace(
        "after the latest", "before the latest"
    )
    assert results[3]["state"]["situation"] == baseline["state"]["situation"].replace(
        "Logs are available but unread.",
        "Logs have been read and identify an expired payment-provider credential as the cause, unrelated to the release.",
    )
    assert results[1]["ranking"][0]["delta_from_baseline"] == (
        None if baseline_fails else pytest.approx(-0.5)
    )
    assert "metrics" not in report
    assert len(requests) == 4
    assert client.is_closed
