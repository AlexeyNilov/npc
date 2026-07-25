from collections.abc import AsyncIterator

from local_llm_project_template.config import LLM_NAME
from local_llm_project_template.infrastructure.chat_client import chat_client


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
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
