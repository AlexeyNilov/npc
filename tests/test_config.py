import importlib

from pytest import MonkeyPatch

from local_llm_project_template import config


def test_uses_defaults_when_environment_variables_are_unset(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_NAME", raising=False)

    loaded_config = importlib.reload(config)

    assert loaded_config.LLM_BASE_URL == "http://127.0.0.1:12345/v1"
    assert loaded_config.LLM_API_KEY == "key"
    assert loaded_config.LLM_NAME == "gemma-4-12b"


def test_uses_environment_variable_overrides(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example.test/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-api-key")
    monkeypatch.setenv("LLM_NAME", "test-model")

    loaded_config = importlib.reload(config)

    assert loaded_config.LLM_BASE_URL == "https://llm.example.test/v1"
    assert loaded_config.LLM_API_KEY == "test-api-key"
    assert loaded_config.LLM_NAME == "test-model"
