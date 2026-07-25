from collections.abc import AsyncIterator

from npc.config import LLM_NAME
from npc.infrastructure.chat_client import chat_client


async def stream_text(prompt: str, system_prompt: str) -> AsyncIterator[str]:
    stream = await chat_client.chat.completions.create(
        model=LLM_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        reasoning_effort="none",
        tool_choice="none",
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


async def complete_text(prompt: str, system_prompt: str) -> str:
    completion = await chat_client.chat.completions.create(
        model=LLM_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        reasoning_effort="none",
        tool_choice="none",
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return completion.choices[0].message.content or ""
