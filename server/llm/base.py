import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)


class LLMError(Exception):
    """Raised when an LLM provider fails."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


def strip_code_fences(text: str) -> str:
    """Strip markdown code fences and thinking tags from LLM responses."""
    text = text.strip()
    # Strip <think>...</think> tags (MiniMax M2.7 reasoning)
    text = re.sub(r"<think>[\s\S]*?</think>\s*", "", text)
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


@runtime_checkable
class LLMProvider(Protocol):
    provider_name: str

    async def complete(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: dict | None = None,
    ) -> LLMResponse: ...
