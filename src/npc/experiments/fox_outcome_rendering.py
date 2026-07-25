import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.fox_distance_feedback import Action, TurnTrace, run_turn

Renderer = Callable[[str], Awaitable[str]]
RenderValidation = Literal["accepted", "invalid_response", "renderer_exception"]
FALLBACK_TEXT = "The fox's response cannot be rendered."
APPROVED_MESSAGES: dict[Action, str] = {
    "flee": "The fox flees.",
    "do_nothing": "The fox does nothing.",
}


@dataclass(frozen=True)
class RenderingTrace:
    canonical_turn: TurnTrace
    prompt: str
    raw_renderer_output: str | None
    validation_result: RenderValidation
    rendered_text: str
    non_authoritative: bool


async def render_completed_turn(canonical_turn: TurnTrace, renderer: Renderer) -> RenderingTrace:
    prompt = _render_prompt(canonical_turn.executed_action)
    try:
        raw_renderer_output = await renderer(prompt)
    except Exception:
        return RenderingTrace(
            canonical_turn=canonical_turn,
            prompt=prompt,
            raw_renderer_output=None,
            validation_result="renderer_exception",
            rendered_text=FALLBACK_TEXT,
            non_authoritative=True,
        )

    validation_result = _validate_response(raw_renderer_output, canonical_turn.executed_action)
    rendered_text = APPROVED_MESSAGES[canonical_turn.executed_action] if validation_result == "accepted" else FALLBACK_TEXT
    return RenderingTrace(
        canonical_turn=canonical_turn,
        prompt=prompt,
        raw_renderer_output=raw_renderer_output,
        validation_result=validation_result,
        rendered_text=rendered_text,
        non_authoritative=True,
    )


async def run_fixture(case: Mapping[str, object]) -> RenderingTrace:
    canonical_turn = await run_turn(
        cast(str, case["player_message"]),
        cast(int, case["starting_distance"]),
        _fixture_turn_completion(case),
    )
    return await render_completed_turn(canonical_turn, _fixture_renderer(case))


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


def _render_prompt(action: Action) -> str:
    return (
        "Completed action: "
        f"{action}. Return JSON with exactly action and message. "
        "You are not choosing an action or asserting a world fact."
    )


def _validate_response(raw_renderer_output: str, action: Action) -> RenderValidation:
    try:
        response = json.loads(raw_renderer_output)
    except json.JSONDecodeError:
        return "invalid_response"
    if not isinstance(response, dict) or set(response) != {"action", "message"}:
        return "invalid_response"
    if response["action"] != action or response["message"] != APPROVED_MESSAGES[action]:
        return "invalid_response"
    return "accepted"


def _fixture_turn_completion(case: Mapping[str, object]) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, __: str) -> str:
        completion = case.get("completion")
        if completion is None:
            raise AssertionError("fixture supplied a completion for an uncalled threat sensor")
        return cast(str, completion)

    return complete


def _fixture_renderer(case: Mapping[str, object]) -> Renderer:
    async def render(_: str) -> str:
        if case.get("renderer_failure") is True:
            raise RuntimeError("fixture renderer unavailable")
        return cast(str, case["renderer_output"])

    return render


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_outcome_rendering.yaml"
    for case in load_corpus(corpus_path):
        print(json.dumps(asdict(await run_fixture(case)), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
