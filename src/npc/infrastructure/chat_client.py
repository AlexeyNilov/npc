from openai import AsyncOpenAI

from npc.config import LLM_API_KEY, LLM_BASE_URL

chat_client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)
