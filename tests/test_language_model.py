import asyncio
from unittest.mock import AsyncMock, Mock

from pytest import MonkeyPatch

from npc.infrastructure import language_model


def test_complete_text_disables_model_thinking(monkeypatch: MonkeyPatch) -> None:
    response = Mock()
    response.choices = [Mock(message=Mock(content="reply"))]
    create = AsyncMock(return_value=response)
    monkeypatch.setattr(language_model.chat_client.chat.completions, "create", create)

    assert asyncio.run(language_model.complete_text("prompt", "system")) == "reply"

    assert create.await_args is not None
    assert create.await_args.kwargs["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}
