from server.llm.openai_provider import OpenAIProvider


class QwenProvider(OpenAIProvider):
    """Qwen uses OpenAI-compatible API at DashScope."""

    provider_name = "qwen"
