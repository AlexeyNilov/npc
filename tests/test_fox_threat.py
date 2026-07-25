import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import cast

from npc.experiments.fox_threat import decide_action, load_corpus, run_case
from npc.experiments.wolf_threat import run_case as run_wolf_case


def candidate(threat: bool, certainty: float, evidence: str | None) -> str:
    return json.dumps({"threat": threat, "certainty": certainty, "evidence": evidence})


def completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def test_same_accepted_candidate_maps_to_flee_for_fox_and_attack_for_wolf() -> None:
    response = candidate(True, 0.7, "I will hurt you")
    fox = asyncio.run(run_case("Fox, I will hurt you.", completion(response)))
    wolf = asyncio.run(run_wolf_case("Wolf, I will hurt you.", completion(response)))

    assert fox.action == "flee"
    assert wolf.action == "attack"


def test_fox_wrapper_makes_one_completion_call() -> None:
    calls = 0

    async def one_response(_: str, __: str) -> str:
        nonlocal calls
        calls += 1
        return candidate(False, 0.5, None)

    asyncio.run(run_case("Hello fox.", one_response))

    assert calls == 1


def test_invalid_and_ungrounded_true_candidates_do_nothing_for_fox() -> None:
    malformed = asyncio.run(run_case("Fox, I will hurt you.", completion("not json")))
    ungrounded = asyncio.run(run_case("Fox, I will hurt you.", completion(candidate(True, 0.7, "I own this forest"))))

    assert malformed.action == "do_nothing"
    assert ungrounded.action == "do_nothing"


def test_fox_policy_is_certainty_invariant() -> None:
    low = asyncio.run(run_case("Fox, I will hurt you.", completion(candidate(True, 0.01, "I will hurt you"))))
    high = asyncio.run(run_case("Fox, I will hurt you.", completion(candidate(True, 0.99, "I will hurt you"))))

    assert decide_action(True) == "flee"
    assert decide_action(False) == "do_nothing"
    assert low.action == high.action == "flee"


def test_checked_in_fox_corpus_has_required_cases_and_expected_fields() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_threat.yaml"
    cases = load_corpus(corpus_path)
    expected_by_id = {case["id"]: case for case in cases}

    assert set(expected_by_id) == {"direct-threat", "calm-greeting", "fearful-plea", "ambiguous-statement"}
    assert {case["expected_threat"] for case in cases} == {True, False}
    assert {case["expected_action"] for case in cases} == {"flee", "do_nothing"}

    for case in cases:
        raw = candidate(cast(bool, case["expected_threat"]), 0.5, _evidence_for(case))
        trace = asyncio.run(run_case(cast(str, case["player_message"]), completion(raw), case))

        assert trace.target == "fox"
        assert trace.expected_threat == case["expected_threat"]
        assert trace.expected_action == case["expected_action"]
        assert trace.action == case["expected_action"]


def _evidence_for(case: dict[str, object]) -> str | None:
    return {"direct-threat": "I will hurt you", "calm-greeting": None, "fearful-plea": None, "ambiguous-statement": None}[
        str(case["id"])
    ]
