"""Choice transport contracts through controlled HTTP responses."""

import json

import httpx2
import pytest

from npc.choice_action_ranking import ChoiceQuestion
from npc.system_one import InvalidEvaluationError, SystemOneError
from npc.system_one_choice import SystemOneChoiceClient

QUESTION = ChoiceQuestion("Choose the best next step", ('read_"logs"', "restart"))
ANSWER = {
    "type": "choice",
    "probabilities": {"action_1": 0.25, "action_0": 0.75},
    "choice": "action_0",
    "confidence": 0.5,
}


INVALID_ANSWERS: tuple[object, ...] = (
    None,
    [],
    {},
    {**ANSWER, "type": "noul"},
    {"type": "choice"},
    {**ANSWER, "probabilities": []},
    {**ANSWER, "probabilities": {}},
    {**ANSWER, "probabilities": {"action_0": 1}},
    {**ANSWER, "probabilities": {"action_0": 1, "unknown": 0}},
    {**ANSWER, "probabilities": {"action_0": 1, "action_1": 0, "extra": 0}},
)


def test_wire_contract_and_lifetime() -> None:
    """One choice request maps opaque option IDs to names and preserves client ownership."""
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200, json={"model": "test", "answers": {"action_choice": ANSWER}}
        )

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneChoiceClient(
            "https://example.test/choice", client=client, timeout=0.5
        )
        assert adapter.model is None
        assert adapter.evaluate_choice({"extra": ""}, QUESTION) == {
            'read_"logs"': 0.75,
            "restart": 0.25,
        }
        assert adapter.model == "test"
        assert not client.is_closed
    assert client.is_closed
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://example.test/choice"
    assert json.loads(request.content) == {
        "state": {"extra": ""},
        "questions": {
            "action_choice": {
                "type": "choice",
                "instructions": QUESTION.instructions,
                "criteria": {"action_0": 'read_"logs"', "action_1": "restart"},
            }
        },
    }
    assert request.extensions["timeout"] == dict.fromkeys(
        ["connect", "read", "write", "pool"], 0.5
    )


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"answers": []},
        {"answers": {}},
        {"answers": {"wrong": ANSWER}},
        {"answers": {"action_choice": ANSWER, "extra": ANSWER}},
        *[{"answers": {"action_choice": answer}} for answer in INVALID_ANSWERS],
    ],
)
def test_invalid_response(payload: object) -> None:
    """Missing, extra, or malformed question/option answers cannot become a ranking."""
    with httpx2.Client(
        transport=httpx2.MockTransport(
            lambda request: httpx2.Response(200, content=json.dumps(payload))
        )
    ) as client:
        with pytest.raises(InvalidEvaluationError):
            SystemOneChoiceClient(
                "http://example.test/choice", client=client
            ).evaluate_choice({}, QUESTION)


@pytest.mark.parametrize(
    ("failure", "detail"),
    [("http", "503"), ("network", "ReadTimeout"), ("json", "JSON")],
)
def test_failures_and_metadata_reset(failure: str, detail: str) -> None:
    """Failures have a stable error boundary and clear metadata from previous requests."""
    calls = 0

    def handle(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx2.Response(
                200, json={"model": "first", "answers": {"action_choice": ANSWER}}
            )
        if failure == "http":
            return httpx2.Response(503, text="private detail")
        if failure == "network":
            raise httpx2.ReadTimeout("private detail", request=request)
        return httpx2.Response(200, text="not json")

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneChoiceClient("http://example.test/choice", client=client)
        adapter.evaluate_choice({}, QUESTION)
        with pytest.raises(SystemOneError) as error:
            adapter.evaluate_choice({}, QUESTION)
        assert detail in str(error.value)
        assert "private detail" not in str(error.value)
        assert adapter.model is None


def test_default_timeout_metadata_and_raw_boundaries() -> None:
    """Default timeout is bounded; absent metadata clears; zero/one scores stay raw."""
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            json={
                "answers": {
                    "action_choice": {
                        "type": "choice",
                        "probabilities": {"action_0": 0, "action_1": 1},
                    }
                }
            },
        )

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneChoiceClient("http://example.test/choice", client=client)
        adapter.model = "stale"
        assert adapter.evaluate_choice({}, QUESTION) == {'read_"logs"': 0, "restart": 1}
        assert adapter.model is None
    assert requests[0].extensions["timeout"] == dict.fromkeys(
        ["connect", "read", "write", "pool"], 30.0
    )


@pytest.mark.parametrize(
    "endpoint", ["", "bad", "ftp://host", "http://host:bad", "http://ho st"]
)
def test_endpoint_validation(endpoint: str) -> None:
    """Invalid complete URLs fail before a request can consume model resources."""
    with httpx2.Client() as client, pytest.raises(ValueError):
        SystemOneChoiceClient(endpoint, client=client)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_timeout_validation(timeout: float) -> None:
    """Every choice request requires a positive finite timeout."""
    with httpx2.Client() as client, pytest.raises(ValueError):
        SystemOneChoiceClient("http://example.test", client=client, timeout=timeout)
