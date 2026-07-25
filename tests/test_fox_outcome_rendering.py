import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path
from typing import cast

from npc.experiments.fox_distance_feedback import run_turn
from npc.experiments.fox_outcome_rendering import load_corpus, render_completed_turn, run_fixture


def threat_candidate() -> str:
    return json.dumps({"threat": True, "certainty": 0.8, "evidence": "I will hurt you"})


def test_renderer_prompt_receives_only_completed_action_and_is_called_once() -> None:
    canonical = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    prompts: list[str] = []

    async def render(prompt: str) -> str:
        prompts.append(prompt)
        return '{"action": "flee", "message": "The fox flees."}'

    trace = asyncio.run(render_completed_turn(canonical, render))

    assert len(prompts) == 1
    assert prompts == [trace.prompt]
    assert "flee" in trace.prompt
    for forbidden in (canonical.player_message, "distance", "candidate", "certainty", "evidence", "heard"):
        assert forbidden not in trace.prompt


def test_valid_completed_actions_render_their_exact_approved_sentence() -> None:
    flee = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    do_nothing = asyncio.run(run_turn("Fox, hello.", 10, _completion('{"threat": false, "certainty": 0.4, "evidence": null}')))

    flee_trace = asyncio.run(render_completed_turn(flee, _renderer('{"action": "flee", "message": "The fox flees."}')))
    non_action_trace = asyncio.run(
        render_completed_turn(do_nothing, _renderer('{"action": "do_nothing", "message": "The fox does nothing."}'))
    )

    assert flee_trace.rendered_text == "The fox flees."
    assert non_action_trace.rendered_text == "The fox does nothing."
    assert non_action_trace.rendered_text != "The fox flees."
    assert flee_trace.validation_result == non_action_trace.validation_result == "accepted"


def test_invalid_mismatched_and_failed_rendering_use_fallback_without_changing_canonical_turn() -> None:
    canonical = asyncio.run(run_turn("Fox, hello.", 10, _completion('{"threat": false, "certainty": 0.4, "evidence": null}')))
    invalid_outputs: list[Callable[[str], Awaitable[str]]] = [
        _renderer("not json"),
        _renderer('{"action": "do_nothing", "message": "The fox does nothing.", "extra": true}'),
        _renderer('{"action": "flee", "message": "The fox flees."}'),
        _renderer('{"action": "do_nothing", "message": "The fox flees."}'),
        _failed_renderer,
    ]

    for renderer in invalid_outputs:
        before = asdict(canonical)
        trace = asyncio.run(render_completed_turn(canonical, renderer))

        assert trace.rendered_text == "The fox's response cannot be rendered."
        assert trace.validation_result != "accepted"
        assert asdict(trace.canonical_turn) == before == asdict(canonical)
        assert trace.canonical_turn.executed_action == "do_nothing"
        assert trace.canonical_turn.resulting_distance == trace.canonical_turn.feedback_distance == 10


def test_rendering_trace_is_complete_json_safe_and_non_authoritative() -> None:
    canonical = asyncio.run(run_turn("Fox, I will hurt you.", 10, _completion(threat_candidate())))
    trace = asyncio.run(render_completed_turn(canonical, _renderer('{"action": "flee", "message": "The fox flees."}')))

    assert set(asdict(trace)) == {
        "canonical_turn",
        "prompt",
        "raw_renderer_output",
        "validation_result",
        "rendered_text",
        "non_authoritative",
    }
    assert trace.canonical_turn == canonical
    assert trace.raw_renderer_output == '{"action": "flee", "message": "The fox flees."}'
    assert trace.non_authoritative is True
    json.dumps(asdict(trace), sort_keys=True)


def test_checked_in_fixtures_cover_completed_turns_and_rendering_failures() -> None:
    corpus_path = Path(__file__).parents[1] / "scenarios" / "fox_outcome_rendering.yaml"
    cases = {cast(str, case["id"]): case for case in load_corpus(corpus_path)}

    assert set(cases) == {
        "accepted-in-range-threat",
        "in-range-non-action",
        "initially-out-of-range-non-action",
        "malformed-renderer-output",
        "renderer-failure",
    }
    traces = {case_id: asyncio.run(run_fixture(case)) for case_id, case in cases.items()}

    assert traces["accepted-in-range-threat"].rendered_text == "The fox flees."
    assert traces["in-range-non-action"].rendered_text == "The fox does nothing."
    assert traces["initially-out-of-range-non-action"].rendered_text == "The fox does nothing."
    assert traces["malformed-renderer-output"].rendered_text == "The fox's response cannot be rendered."
    assert traces["renderer-failure"].raw_renderer_output is None
    assert traces["renderer-failure"].rendered_text == "The fox's response cannot be rendered."

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
