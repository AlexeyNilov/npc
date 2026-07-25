import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path
from typing import cast

from pytest import MonkeyPatch

from npc.experiments import fox_outcome_rendering
from npc.experiments.fox_distance_feedback import run_turn
from npc.experiments.fox_outcome_rendering import (
    FALLBACK_TEXT,
    configured_narrator,
    load_corpus,
    render_completed_turn,
    run_fixture,
)


def threat_candidate() -> str:
    return json.dumps({"threat": True, "certainty": 0.8, "evidence": "I will hurt you"})


def test_configured_narrator_receives_only_completed_action_and_is_called_once(monkeypatch: MonkeyPatch) -> None:
    canonical = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    calls: list[tuple[str, str]] = []

    async def complete_text(prompt: str, instruction: str) -> str:
        calls.append((prompt, instruction))
        return "The fox darts into the undergrowth."

    monkeypatch.setattr(fox_outcome_rendering, "complete_text", complete_text)
    trace = asyncio.run(render_completed_turn(canonical, configured_narrator))

    assert len(calls) == 1
    assert calls[0][0] == trace.prompt
    assert "flee" in trace.prompt
    for forbidden in (canonical.player_message, "distance", "candidate", "certainty", "evidence", "heard"):
        assert forbidden not in trace.prompt
        assert forbidden not in calls[0][1]


def test_nonblank_freeform_completed_actions_render_as_returned() -> None:
    flee = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    do_nothing = asyncio.run(run_turn("Fox, hello.", 10, _completion('{"threat": false, "certainty": 0.4, "evidence": null}')))

    flee_trace = asyncio.run(render_completed_turn(flee, _renderer("The fox vanishes through the brush.")))
    non_action_trace = asyncio.run(render_completed_turn(do_nothing, _renderer("The fox watches in silence.")))

    assert flee_trace.rendered_text == "The fox vanishes through the brush."
    assert non_action_trace.rendered_text == "The fox watches in silence."
    assert flee_trace.validation_result == non_action_trace.validation_result == "accepted"


def test_blank_oversized_and_failed_rendering_use_fallback_without_changing_canonical_turn() -> None:
    canonical = asyncio.run(run_turn("Fox, hello.", 10, _completion('{"threat": false, "certainty": 0.4, "evidence": null}')))
    invalid_outputs: list[Callable[[str], Awaitable[str]]] = [
        _renderer(""),
        _renderer("   "),
        _renderer("x" * 281),
        _failed_renderer,
    ]

    for renderer in invalid_outputs:
        before = asdict(canonical)
        trace = asyncio.run(render_completed_turn(canonical, renderer))

        assert trace.rendered_text == FALLBACK_TEXT
        assert trace.validation_result != "accepted"
        assert asdict(trace.canonical_turn) == before == asdict(canonical)
        assert trace.canonical_turn is not canonical
        assert trace.canonical_turn.executed_action == "do_nothing"
        assert trace.canonical_turn.resulting_distance == trace.canonical_turn.feedback_distance == 10


def test_rendering_trace_is_complete_json_safe_and_non_authoritative() -> None:
    canonical = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    trace = asyncio.run(render_completed_turn(canonical, _renderer("The fox retreats.")))

    assert set(asdict(trace)) == {
        "canonical_turn",
        "prompt",
        "raw_renderer_output",
        "validation_result",
        "rendered_text",
        "non_authoritative",
    }
    assert trace.canonical_turn == canonical
    assert trace.raw_renderer_output == "The fox retreats."
    assert trace.non_authoritative is True
    json.dumps(asdict(trace), sort_keys=True)


def test_checked_in_fixtures_cover_completed_turns_and_rendering_failures() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_outcome_rendering.yaml"
    cases = {cast(str, case["id"]): case for case in load_corpus(corpus_path)}

    assert set(cases) == {
        "freeform-in-range-flee",
        "freeform-in-range-do-nothing",
        "blank-narration",
        "oversized-narration",
        "narrator-failure",
    }
    traces = {case_id: asyncio.run(run_fixture(case)) for case_id, case in cases.items()}

    assert traces["freeform-in-range-flee"].rendered_text == "The fox bolts into the trees."
    assert traces["freeform-in-range-do-nothing"].rendered_text == "The fox pauses, then stays put."
    assert traces["blank-narration"].rendered_text == FALLBACK_TEXT
    assert traces["oversized-narration"].rendered_text == FALLBACK_TEXT
    assert traces["narrator-failure"].raw_renderer_output is None
    assert traces["narrator-failure"].rendered_text == FALLBACK_TEXT

    for case_id, trace in traces.items():
        assert trace.canonical_turn.executed_action == cases[case_id]["expected_action"]
        assert trace.canonical_turn.resulting_distance == cases[case_id]["expected_resulting_distance"]


def _completion(response: str) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        return response

    return complete


def _renderer(response: str) -> Callable[[str], Awaitable[str]]:
    async def render(_: str) -> str:
        return response

    return render


async def _failed_renderer(_: str) -> str:
    raise RuntimeError("fixture renderer unavailable")
