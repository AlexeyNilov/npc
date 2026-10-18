"""HTTP adapter contracts using controlled HTTPX2 transports."""

import json

import httpx2
import pytest

from npc.model.evaluation import ChoiceQuestion, Question
from npc.system_one import InvalidEvaluationError, SystemOneClient, SystemOneError

ENDPOINT = "http://127.0.0.1:12346/v1/systemone"
QUESTIONS: dict[str, Question] = {
    "action_0": {"type": "noul", "instructions": "Useful?"}
}


def test_one_client_can_alternate_question_types() -> None:
    """Both methods share transport ownership and reset metadata on each request."""
    payloads = [
        {"model": "first", "answers": {"action_0": {"type": "noul", "noul": 0.8}}},
        {
            "answers": {
                "action_choice": {"type": "choice", "probabilities": {"action_0": 1}}
            }
        },
        {"model": "third", "answers": {"action_0": {"type": "noul", "noul": 0.2}}},
    ]
    with httpx2.Client(
        transport=httpx2.MockTransport(
            lambda request: httpx2.Response(200, json=payloads.pop(0))
        )
    ) as client:
        evaluator = SystemOneClient(ENDPOINT, client=client)
        assert evaluator.evaluate({}, QUESTIONS) == {"action_0": 0.8}
        assert evaluator.model == "first"
        assert evaluator.evaluate_choice(
            {}, ChoiceQuestion("Choose", ("inspect",))
        ) == {"inspect": 1.0}
        assert evaluator.model is None
        assert evaluator.evaluate({}, QUESTIONS) == {"action_0": 0.2}
        assert evaluator.model == "third"
        assert not client.is_closed


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
        assert adapter.evaluate(
            {"intent": "goal", "situation": "state"}, QUESTIONS
        ) == {"action_0": 0.8}
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
    [
        "",
        " ",
        "/v1/systemone",
        "ftp://host/path",
        "http://ho st",
        "http://",
        "http://host:bad/path",
    ],
)
def test_invalid_endpoint(endpoint: str) -> None:
    """Configuration errors are rejected before sending a request."""
    with httpx2.Client() as client, pytest.raises(ValueError, match="(?i)HTTP"):
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
        with pytest.raises(SystemOneError, match=failure.__name__):
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
    ]
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=payloads.pop(0))

    with httpx2.Client(transport=httpx2.MockTransport(handle)) as client:
        adapter = SystemOneClient("https://example.test/v1/systemone", client=client)
        adapter.evaluate({}, {})
        assert adapter.model == "first"
        for _ in range(2):
            adapter.evaluate({}, {})
            assert adapter.model is None
    assert str(requests[0].url) == "https://example.test/v1/systemone"
    assert requests[0].extensions["timeout"] == dict(
        connect=30.0, read=30.0, write=30.0, pool=30.0
    )


def test_short_positive_timeout() -> None:
    """Positive subsecond timeouts are allowed and metadata starts absent."""
    with httpx2.Client() as client:
        adapter = SystemOneClient(ENDPOINT, client=client, timeout=0.1)
        assert adapter.model is None


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"answers": []},
        {"answers": {}},
        {"answers": {"other_id": {"type": "noul", "noul": 0.5}}},
        {"answers": {"action_0": {"type": "choice", "noul": 0.5}}},
        {"answers": {"action_0": {"noul": 0.5}}},
        {"answers": {"action_0": None}},
        {"answers": {"action_0": {"type": "noul"}}},
        {
            "answers": {
                "action_0": {"type": "noul", "noul": 0.5},
                "extra": {"type": "noul", "noul": 0.8},
            }
        },
    ],
)
def test_invalid_answer_contract(payload: object) -> None:
    """Malformed, missing or extra service answers cannot escape as domain scores."""
    with httpx2.Client(
        transport=httpx2.MockTransport(
            lambda request: httpx2.Response(200, content=json.dumps(payload))
        )
    ) as client:
        with pytest.raises(InvalidEvaluationError) as error:
            SystemOneClient(ENDPOINT, client=client).evaluate({}, QUESTIONS)
        assert str(error.value) not in {"", "None"}


def test_decoded_probabilities_match_ids_and_preserve_boundaries() -> None:
    """Service answers become raw domain probabilities regardless of response order."""
    questions: dict[str, Question] = {
        key: {"type": "noul", "instructions": "Useful?"}
        for key in ("first", "second", "third")
    }
    payload = {
        "answers": {
            "third": {"type": "noul", "noul": 1},
            "second": {"type": "noul", "noul": 0.25},
            "first": {"type": "noul", "noul": 0},
        }
    }
    with httpx2.Client(
        transport=httpx2.MockTransport(
            lambda request: httpx2.Response(200, content=json.dumps(payload))
        )
    ) as client:
        assert SystemOneClient(ENDPOINT, client=client).evaluate({}, questions) == {
            "first": 0.0,
            "second": 0.25,
            "third": 1.0,
        }
