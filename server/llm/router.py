import logging

from server.config import settings
from server.llm.base import LLMError, LLMProvider, LLMResponse, Message
from server.llm.gemini_provider import GeminiProvider
from server.llm.minimax_provider import MiniMaxProvider
from server.llm.openai_provider import OpenAIProvider
from server.llm.qwen_provider import QwenProvider

logger = logging.getLogger(__name__)

# Agents that need deep thinking (Mirror translation, detection, Advisor)
DEEP_THINKING_AGENTS = {"mirror", "advisor", "arbiter", "advocate", "cross_examination"}
# Agents that only need structured parsing (fast, no deep reasoning)
FAST_AGENTS = {"intake", "clarification", "health", "memory", "drift", "escalation"}


class LLMRouter:
    """Routes LLM calls to configured providers with fallback support."""

    def __init__(self):
        self._providers: list[LLMProvider] = []
        self._agent_overrides: dict[str, str] = {}
        self._provider_map: dict[str, LLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        # Primary: OpenAI
        if settings.openai_api_key:
            provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model=settings.openai_model,
            )
            self._providers.append(provider)
            self._provider_map["openai"] = provider

        # Fallback 1: Qwen
        if settings.qwen_api_key:
            provider = QwenProvider(
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url,
                model=settings.qwen_model,
            )
            self._providers.append(provider)
            self._provider_map["qwen"] = provider

        # Fallback 2: Gemini
        if settings.gemini_api_key:
            provider = GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
            )
            self._providers.append(provider)
            self._provider_map["gemini"] = provider

        # Fallback 3: MiniMax
        if settings.minimax_api_key:
            provider = MiniMaxProvider(
                api_key=settings.minimax_api_key,
                group_id=settings.minimax_group_id,
                model=settings.minimax_model,
            )
            self._providers.append(provider)
            self._provider_map["minimax"] = provider

    def _get_provider(self, agent_name: str | None = None) -> LLMProvider:
        if agent_name and agent_name in self._agent_overrides:
            provider_name = self._agent_overrides[agent_name]
            if provider_name in self._provider_map:
                return self._provider_map[provider_name]

        if not self._providers:
            raise LLMError("router", "No LLM providers configured. Set at least one API key.")
        return self._providers[0]

    def _get_thinking_mode(self, agent_name: str | None) -> str:
        """Determine thinking mode based on agent type."""
        if agent_name and agent_name in FAST_AGENTS:
            return "disabled"
        return "enabled"

    async def complete(
        self,
        messages: list[Message],
        agent_name: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: dict | None = None,
    ) -> LLMResponse:
        errors: list[str] = []
        thinking_mode = self._get_thinking_mode(agent_name)

        # Build extra kwargs for MiniMax thinking control
        extra_kwargs: dict = {}
        extra_kwargs["thinking_mode"] = thinking_mode

        # Try the preferred provider first
        preferred = self._get_provider(agent_name)
        try:
            if isinstance(preferred, MiniMaxProvider):
                return await preferred.complete(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    thinking_mode=thinking_mode,
                )
            return await preferred.complete(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
        except LLMError as e:
            errors.append(str(e))
            logger.warning("Primary provider failed: %s", e)

        # Try fallbacks
        for provider in self._providers:
            if provider is preferred:
                continue
            try:
                logger.info("Trying fallback provider: %s", provider.provider_name)
                if isinstance(provider, MiniMaxProvider):
                    return await provider.complete(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        thinking_mode=thinking_mode,
                    )
                return await provider.complete(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            except LLMError as e:
                errors.append(str(e))
                logger.warning("Fallback provider failed: %s", e)

        raise LLMError("router", f"All providers failed: {'; '.join(errors)}")


# Singleton instance
llm_router = LLMRouter()
