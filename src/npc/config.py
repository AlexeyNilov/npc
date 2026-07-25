import os

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:12345/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "key")
LLM_NAME = os.getenv("LLM_NAME", "gemma-4-12b")
