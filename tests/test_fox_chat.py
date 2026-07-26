import asyncio
from collections.abc import Iterator

import pytest
from pytest import CaptureFixture, MonkeyPatch

from sample.fox_chat import chat, chat_turn


def test_chat_turn_runs_the_fox_pipeline_then_renders_non_authoritative_outcome() -> None:
    sensor_calls: list[tuple[str, str]] = []
    narrator_prompts: list[str] = []

    async def complete(prompt: str, instruction: str) -> str:
        sensor_calls.append((prompt, instruction))
        return '{"threat": true, "certainty": 0.8, "evidence": "I will hurt you"}'

    async def narrate(prompt: str) -> str:
        narrator_prompts.append(prompt)
        return "The fox slips behind the trees."

    trace = asyncio.run(chat_turn("Fox, I will hurt you.", 10, complete, narrate))

    assert len(sensor_calls) == 2
    assert trace.canonical_turn.executed_action == "flee"
    assert trace.canonical_turn.feedback_distance == 15
    assert narrator_prompts == [trace.prompt]
    assert trace.rendered_text == "The fox slips behind the trees."
    assert trace.non_authoritative is True


def test_chat_turn_carries_distance_and_does_not_turn_narration_into_next_turn_input() -> None:
    async def complete(_: str, __: str) -> str:
        return '{"threat": false, "certainty": 0.4, "evidence": null}'

    async def narrate(_: str) -> str:
        return "The fox watches without moving."

    first = asyncio.run(chat_turn("Fox, hello.", 10, complete, narrate))
    second = asyncio.run(chat_turn("Fox, hello again.", first.canonical_turn.feedback_distance, complete, narrate))

    assert first.canonical_turn.feedback_distance == second.canonical_turn.starting_distance == 10
    assert second.canonical_turn.player_message == "Fox, hello again."
    assert "watches" not in second.canonical_turn.player_message


def test_chat_prints_explicit_non_authoritative_narration_and_authoritative_feedback_distance_after_each_turn(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    messages: Iterator[str] = iter(["Fox, I will hurt you.", "/exit"])

    async def complete(_: str, __: str) -> str:
        return '{"threat": true, "certainty": 0.8, "evidence": "I will hurt you"}'

    async def narrate(_: str) -> str:
        return "The fox disappears into the trees."

    monkeypatch.setattr("builtins.input", lambda _: next(messages))

    asyncio.run(chat(10, complete, narrate))

    output = capsys.readouterr().out
    assert "Narration (non-authoritative): The fox disappears into the trees." in output
    assert "Fox:" not in output
    assert "Distance: 15" in output


def test_chat_turn_carries_authoritative_approach_distance() -> None:
    async def complete(_: str, prompt: str) -> str:
        if "hostile threat" in prompt:
            return '{"threat": false, "certainty": 0.8, "evidence": null}'
        return '{"food_offer": true, "certainty": 0.8, "evidence": "I offer you this fresh meat"}'

    async def narrate(_: str) -> str:
        return "The fox edges nearer."

    trace = asyncio.run(chat_turn("Fox, I offer you this fresh meat.", 10, complete, narrate))

    assert trace.canonical_turn.executed_action == "approach"
    assert trace.canonical_turn.feedback_distance == 7


def test_chat_turn_rejects_invalid_starting_distance_before_completion_or_narration() -> None:
    completion_calls = 0
    narration_calls = 0

    async def complete(_: str, __: str) -> str:
        nonlocal completion_calls
        completion_calls += 1
        return "not used"

    async def narrate(_: str) -> str:
        nonlocal narration_calls
        narration_calls += 1
        return "not used"

    with pytest.raises(ValueError):
        asyncio.run(chat_turn("Fox, hello.", -1, complete, narrate))

    assert completion_calls == narration_calls == 0
