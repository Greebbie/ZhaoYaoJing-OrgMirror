from unittest.mock import AsyncMock, patch

import pytest

from server.llm.base import LLMError, LLMResponse, Message
from server.llm.router import LLMRouter


@pytest.fixture
def mock_settings():
    with patch("server.llm.router.settings") as mock:
        mock.openai_api_key = "test-key"
        mock.openai_base_url = "https://api.openai.com/v1"
        mock.openai_model = "gpt-4o"
        mock.qwen_api_key = "test-qwen-key"
        mock.qwen_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        mock.qwen_model = "qwen-max"
        mock.gemini_api_key = ""
        mock.minimax_api_key = ""
        mock.minimax_group_id = ""
        mock.minimax_model = ""
        mock.gemini_model = ""
        yield mock


def test_router_initializes_providers(mock_settings):
    router = LLMRouter()
    assert len(router._providers) == 2  # OpenAI + Qwen


def test_router_no_providers():
    with patch("server.llm.router.settings") as mock:
        mock.openai_api_key = ""
        mock.qwen_api_key = ""
        mock.gemini_api_key = ""
        mock.minimax_api_key = ""
        mock.minimax_group_id = ""
        mock.minimax_model = ""
        mock.gemini_model = ""
        router = LLMRouter()
        assert len(router._providers) == 0


@pytest.mark.asyncio
async def test_router_fallback(mock_settings):
    router = LLMRouter()

    # Make primary fail
    router._providers[0].complete = AsyncMock(
        side_effect=LLMError("openai", "rate limited")
    )
    # Make fallback succeed
    expected = LLMResponse(content="hello", model="qwen-max", provider="qwen")
    router._providers[1].complete = AsyncMock(return_value=expected)

    messages = [Message(role="user", content="test")]
    result = await router.complete(messages)
    assert result.provider == "qwen"
    assert result.content == "hello"


@pytest.mark.asyncio
async def test_router_all_fail(mock_settings):
    router = LLMRouter()

    for p in router._providers:
        p.complete = AsyncMock(side_effect=LLMError(p.provider_name, "failed"))

    messages = [Message(role="user", content="test")]
    with pytest.raises(LLMError, match="All providers failed"):
        await router.complete(messages)
