"""HTTP adapter contracts using controlled HTTPX2 transports."""

import json

import httpx2
import pytest

from npc.action_ranking import Question
from npc.system_one import SystemOneClient, SystemOneError

ENDPOINT = "http://127.0.0.1:12346/v1/systemone"
QUESTIONS: dict[str, Question] = {
    "action_0": {"type": "noul", "instructions": "Useful?"}
}


def test_exact_request_and_metadata() -> None:
    """POST to the full configured endpoint with typed questions and finite timeout."""
    requests: list[httpx2.Request] = []
    payload = {
        "model": "decision-test",
        "answers": {"action_0": {"type": "noul", "noul": 0.8}},
    }

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=payload)

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneClient(ENDPOINT, client=client, timeout=7.0)
        assert (
            adapter.evaluate({"intent": "goal", "situation": "state"}, QUESTIONS)
            == payload
        )
        assert adapter.model == "decision-test"
        assert not client.is_closed
    assert client.is_closed
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == ENDPOINT
    assert request.headers["content-type"] == "application/json"
    assert json.loads(request.content) == {
        "state": {"intent": "goal", "situation": "state"},
        "questions": QUESTIONS,
    }
    assert request.extensions["timeout"] == dict(
        connect=7.0, read=7.0, write=7.0, pool=7.0
    )


@pytest.mark.parametrize(
    "endpoint",
    ["", " ", "/v1/systemone", "ftp://host/path", "http://", "http://host:bad/path"],
)
def test_invalid_endpoint(endpoint: str) -> None:
    """Configuration errors are rejected before sending a request."""
    with httpx2.Client() as client, pytest.raises(ValueError):
        SystemOneClient(endpoint, client=client)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_invalid_timeout(timeout: float) -> None:
    """All HTTP calls require a positive finite timeout."""
    with httpx2.Client() as client, pytest.raises(ValueError):
        SystemOneClient(ENDPOINT, client=client, timeout=timeout)


@pytest.mark.parametrize("status", [400, 501, 503, 302])
def test_http_errors(status: int) -> None:
    """Unsuccessful HTTP statuses surface without leaking response contents."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(status, text="private upstream detail")

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        with pytest.raises(SystemOneError, match=str(status)) as error:
            SystemOneClient(ENDPOINT, client=client).evaluate({}, QUESTIONS)
    assert "private upstream detail" not in str(error.value)


@pytest.mark.parametrize("failure", [httpx2.ReadTimeout, httpx2.ConnectError])
def test_transport_errors(failure: type[httpx2.RequestError]) -> None:
    """Transport failures have a stable dependency error boundary."""

    def handle(request: httpx2.Request) -> httpx2.Response:
        raise failure("unavailable", request=request)

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        with pytest.raises(SystemOneError, match="request failed"):
            SystemOneClient(ENDPOINT, client=client).evaluate({}, QUESTIONS)


def test_bad_json_and_closed_response() -> None:
    """Invalid JSON is a dependency failure and the response is still closed."""
    response = httpx2.Response(200, content=b"not json")
    with httpx2.Client(
        transport=httpx2.MockTransport(lambda request: response)
    ) as client:
        with pytest.raises(SystemOneError, match="JSON"):
            SystemOneClient(ENDPOINT, client=client).evaluate({}, QUESTIONS)
    assert response.is_closed


def test_https_and_default_timeout_and_metadata_reset() -> None:
    """HTTPS works, default timeout is bounded, and absent metadata never goes stale."""
    payloads: list[object] = [
        {"model": "first", "answers": {}},
        {"answers": {}},
        {"model": 123, "answers": {}},
        [],
    ]
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=payloads.pop(0))

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneClient("https://example.test/v1/systemone", client=client)
        adapter.evaluate({}, {})
        assert adapter.model == "first"
        for _ in range(3):
            adapter.evaluate({}, {})
            assert adapter.model is None
    assert str(requests[0].url) == "https://example.test/v1/systemone"
    assert requests[0].extensions["timeout"] == dict(
        connect=30.0, read=30.0, write=30.0, pool=30.0
    )
