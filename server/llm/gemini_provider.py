from server.llm.base import LLMError, LLMResponse, Message


class GeminiProvider:
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: dict | None = None,
    ) -> LLMResponse:
        raise LLMError(self.provider_name, "Gemini provider not yet implemented")
