"""Contracts for the single-request action ranking command."""

import io
import json
import tomllib
from pathlib import Path

import httpx2
import pytest

from npc.cli.action_ranking import main

STATE = {
    "intent": " Restore checkout ",
    "situation": " Cause unknown ",
    "recent_events": "A release just completed.",
}

REQUEST = {
    "state": STATE,
    "actions": [" Read logs ", "Roll back", "Write docs"],
}
INVALID_ARRAYS: tuple[object, ...] = (None, "Read logs", {})


@pytest.fixture
def stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a valid request without depending on a terminal."""
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(REQUEST)))


@pytest.mark.parametrize("source", ["stdin", "dash", "file", "default-timeout"])
def test_ranking(
    source: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stdin: None,
) -> None:
    """Every input source yields raw scores, stable ties, and trimmed action names."""
    requests: list[httpx2.Request] = []
    clients: list[httpx2.Client] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            json={
                "answers": {
                    f"action_{i}": {"type": "noul", "noul": score}
                    for i, score in enumerate([0.123456789, 1, 1])
                }
            },
        )

    real_client = httpx2.Client

    def factory() -> httpx2.Client:
        client = real_client(transport=httpx2.MockTransport(handle))
        clients.append(client)
        return client

    monkeypatch.setattr("npc.cli.action_ranking.httpx2.Client", factory)
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/rank")
    args = ["--timeout", "0.5"]
    if source == "dash":
        args += ["--input", "-"]
    elif source == "file":
        path = tmp_path / "request.json"
        path.write_text(json.dumps(REQUEST), encoding="utf-8")
        args += ["--input", str(path)]
        monkeypatch.setattr("sys.stdin", io.StringIO("invalid stdin"))
    elif source == "default-timeout":
        args = []
    assert main(args) == 0
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out) == [
        {"action": "Roll back", "score": 1.0},
        {"action": "Write docs", "score": 1.0},
        {"action": "Read logs", "score": 0.123456789},
    ]
    assert len(requests) == 1
    assert str(requests[0].url) == "http://example.test/rank"
    assert json.loads(requests[0].content)["state"] == {
        **STATE,
        "available_actions": json.dumps(["Read logs", "Roll back", "Write docs"]),
    }
    assert requests[0].extensions["timeout"] == dict.fromkeys(
        ["connect", "read", "write", "pool"],
        30.0 if source == "default-timeout" else 0.5,
    )
    assert clients[0].is_closed


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        {},
        {**REQUEST, "extra": 1},
        {**REQUEST, "state": "old situation input"},
        {**REQUEST, "state": {**STATE, "extra": 1}},
        {**REQUEST, "state": {**STATE, "available_actions": "[]"}},
        *[{k: v for k, v in REQUEST.items() if k != field} for field in REQUEST],
        *[{**REQUEST, "actions": value} for value in INVALID_ARRAYS],
        {**REQUEST, "state": {**STATE, "intent": ""}, "actions": []},
    ],
)
def test_invalid_input(
    value: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Bad JSON shapes and invalid domain inputs fail before HTTP configuration."""
    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(value)))
    assert main([]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "Invalid input:" in output.err


@pytest.mark.parametrize("text", ["{", "{} {}", ""])
def test_bad_json(
    text: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Malformed or multiple documents produce an input error and no ranking."""
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    assert main([]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "Invalid input:" in output.err


def test_empty(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A valid empty catalog needs neither endpoint configuration nor a client."""
    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    monkeypatch.setattr(
        "sys.stdin", io.StringIO(json.dumps({**REQUEST, "actions": []}))
    )

    def unexpected_client() -> None:
        pytest.fail("An empty catalog must not create an HTTP client")

    monkeypatch.setattr("npc.cli.action_ranking.httpx2.Client", unexpected_client)
    assert main([]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == []
    assert output.err == ""


def test_oversized_catalog(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Oversized input is diagnosed before endpoint configuration or client creation."""
    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(
            json.dumps(
                {**REQUEST, "actions": [f"action_{index}" for index in range(11)]}
            )
        ),
    )

    def unexpected_client() -> None:
        pytest.fail("An oversized catalog must not create an HTTP client")

    monkeypatch.setattr("npc.cli.action_ranking.httpx2.Client", unexpected_client)
    assert main([]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "Invalid input:" in output.err
    assert "11" in output.err
    assert "10" in output.err


@pytest.mark.parametrize("endpoint", [None, "bad-url"])
def test_configuration(
    endpoint: str | None,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin: None,
) -> None:
    """Configuration errors are distinguishable from invalid input."""
    monkeypatch.delenv("SYSTEM_ONE", raising=False)
    if endpoint is not None:
        monkeypatch.setenv("SYSTEM_ONE", endpoint)
    assert main([]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "Configuration error:" in output.err


@pytest.mark.parametrize("timeout", ["0", "-1", "inf", "nan", "text"])
def test_timeout(timeout: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Invalid timeout arguments are rejected before reading stdin."""
    with pytest.raises(SystemExit) as error:
        main(["--timeout", timeout])
    assert error.value.code == 2
    assert "timeout" in capsys.readouterr().err


@pytest.mark.parametrize("failure", ["http", "network", "json", "answers"])
def test_evaluation_failure(
    failure: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin: None,
) -> None:
    """Dependency and response failures emit no partial result and close the client."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        if failure == "network":
            raise httpx2.ConnectError("offline", request=request)
        if failure == "http":
            return httpx2.Response(503)
        if failure == "json":
            return httpx2.Response(200, text="invalid")
        return httpx2.Response(200, json={"answers": {}})

    client = httpx2.Client(transport=httpx2.MockTransport(handle))
    monkeypatch.setattr("npc.cli.action_ranking.httpx2.Client", lambda: client)
    monkeypatch.setenv("SYSTEM_ONE", "http://example.test/rank")
    assert main([]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    category = "Invalid response:" if failure == "answers" else "Dependency error:"
    assert category in output.err
    assert client.is_closed


def test_file_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Unreadable files and invalid UTF-8 are reported as I/O errors."""
    path = tmp_path / "request.json"
    assert main(["--input", str(path)]) == 1
    path.write_bytes(b"\xff")
    assert main(["--input", str(path)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.count("I/O error:") == 2


def test_entrypoint() -> None:
    """Installation exposes the agreed executable name and callable."""
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert config["project"]["scripts"]["npc-rank-actions"] == (
        "npc.cli.action_ranking:main"
    )


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Help documents the JSON contract and configuration without reading input."""
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    output = capsys.readouterr()
    assert output.err == ""
    for term in (
        "--input",
        "--timeout",
        "intent",
        "situation",
        "state",
        "Additional state fields",
        "available_actions",
        "actions",
        "score",
        "SYSTEM_ONE",
        "Exit codes",
        "30",
        "10",
        "stdin",
    ):
        assert term in output.out


@pytest.mark.parametrize(
    ("value", "detail"),
    [
        ({}, "state and actions"),
        ({**REQUEST, "actions": None}, "actions must be an array"),
        (
            {**REQUEST, "state": {"intent": "goal", "situation": " "}},
            "nonblank strings",
        ),
        ({**REQUEST, "actions": ["a", " a "]}, "unique"),
    ],
)
def test_actionable_input_error(
    value: object,
    detail: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Input diagnostics explain what callers must correct."""
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(value)))
    assert main([]) == 2
    assert detail in capsys.readouterr().err


def test_output_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A closed output pipe produces an I/O failure rather than a traceback."""

    class BrokenOutput(io.StringIO):
        def write(self, text: str) -> int:
            raise BrokenPipeError("closed pipe")

    monkeypatch.setattr(
        "sys.stdin", io.StringIO(json.dumps({**REQUEST, "actions": []}))
    )
    monkeypatch.setattr("sys.stdout", BrokenOutput())
    assert main([]) == 1
    assert "I/O error: closed pipe" in capsys.readouterr().err
