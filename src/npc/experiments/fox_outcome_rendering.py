import argparse
import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.experiments.fox_deterministic_utility import TurnTrace as UtilityTurnTrace
from npc.experiments.fox_distance_feedback import Action, TurnTrace, run_turn
from npc.infrastructure.language_model import complete_text

Renderer = Callable[[str], Awaitable[str]]
RenderValidation = Literal["accepted", "unusable_response", "narrator_exception"]
CompletedFoxTurn = TurnTrace | UtilityTurnTrace
FALLBACK_TEXT = "The fox's response cannot be rendered."
MAX_NARRATION_CHARACTERS = 280
NARRATOR_INSTRUCTION = (
    "Narration is non-authoritative presentation only. Best-effort narrate only the completed fox action. "
    "When the prompt supplies authoritative hunger, you may use it as expressive prose context for the fox's food-seeking, "
    "but this interpretation is not authoritative. "
    "Do not make claims unsupported by the completed action or supplied hunger, including dialogue, unseen events, "
    "locations, or world state. "
    "Do not choose an action or change world state, outcome, or feedback."
)


@dataclass(frozen=True)
class RenderingTrace:
    canonical_turn: CompletedFoxTurn
    prompt: str
    raw_renderer_output: str | None
    validation_result: RenderValidation
    rendered_text: str
    non_authoritative: bool


async def render_completed_turn(canonical_turn: CompletedFoxTurn, renderer: Renderer) -> RenderingTrace:
    resulting_hunger = canonical_turn.resulting_hunger if isinstance(canonical_turn, UtilityTurnTrace) else None
    prompt = _render_prompt(canonical_turn.executed_action, resulting_hunger)
    preserved_turn = replace(canonical_turn)
    try:
        raw_renderer_output = await renderer(prompt)
    except Exception:
        return RenderingTrace(
            canonical_turn=preserved_turn,
            prompt=prompt,
            raw_renderer_output=None,
            validation_result="narrator_exception",
            rendered_text=FALLBACK_TEXT,
            non_authoritative=True,
        )

    validation_result = _validate_response(raw_renderer_output)
    rendered_text = raw_renderer_output if validation_result == "accepted" else FALLBACK_TEXT
    return RenderingTrace(
        canonical_turn=preserved_turn,
        prompt=prompt,
        raw_renderer_output=raw_renderer_output,
        validation_result=validation_result,
        rendered_text=rendered_text,
        non_authoritative=True,
    )


async def run_fixture(case: Mapping[str, object]) -> RenderingTrace:
    canonical_turn = await _fixture_canonical_turn(case)
    return await render_completed_turn(canonical_turn, _fixture_renderer(case))


async def run_configured_fixture(case: Mapping[str, object]) -> RenderingTrace:
    """Render a fixture-produced canonical turn with the configured narrator."""
    return await render_completed_turn(await _fixture_canonical_turn(case), configured_narrator)


async def configured_narrator(prompt: str) -> str:
    """Fox-local adapter for the configured, non-authoritative narrator."""
    return await complete_text(prompt, NARRATOR_INSTRUCTION)


def load_corpus(path: Path) -> list[dict[str, object]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, object], case) for case in cast(list[dict[str, object]], data["cases"])]


def _render_prompt(action: Action, resulting_hunger: int | None = None) -> str:
    hunger = f" Authoritative fox hunger after the action: {resulting_hunger}/100." if resulting_hunger is not None else ""
    return f"Completed fox action: {action}.{hunger} Provide concise player-facing narration."


def _validate_response(raw_renderer_output: str) -> RenderValidation:
    if not raw_renderer_output.strip() or len(raw_renderer_output) > MAX_NARRATION_CHARACTERS:
        return "unusable_response"
    return "accepted"


async def _fixture_canonical_turn(case: Mapping[str, object]) -> TurnTrace:
    return await run_turn(
        cast(str, case["player_message"]),
        cast(int, case["starting_distance"]),
        _fixture_turn_completion(case),
    )


def _fixture_turn_completion(case: Mapping[str, object]) -> Callable[[str, str], Awaitable[str]]:
    async def complete(_: str, prompt: str) -> str:
        completion = case.get("threat_completion") if "hostile threat" in prompt else case.get("food_offer_completion")
        if completion is None:
            raise AssertionError("fixture supplied a completion for an uncalled sensor")
        return cast(str, completion)

    return complete


def _fixture_renderer(case: Mapping[str, object]) -> Renderer:
    async def render(_: str) -> str:
        if case.get("renderer_failure") is True:
            raise RuntimeError("fixture renderer unavailable")
        return cast(str, case["renderer_output"])

    return render


async def main_async() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configured-narrator", action="store_true")
    args = parser.parse_args()
    corpus_path = Path(__file__).parents[3] / "scenarios" / "fox_outcome_rendering.yaml"
    for case in load_corpus(corpus_path):
        trace = await (run_configured_fixture(case) if args.configured_narrator else run_fixture(case))
        print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
