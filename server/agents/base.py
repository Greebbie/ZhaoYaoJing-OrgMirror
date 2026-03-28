import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from server.llm.base import Message, strip_code_fences
from server.llm.router import LLMRouter

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class AgentContext(dict):
    """Accumulated context passed between agents in a pipeline."""


class AgentResult:
    """Result from an agent execution."""

    def __init__(self, data: dict[str, Any], agent_name: str, elapsed_ms: float):
        self.data = data
        self.agent_name = agent_name
        self.elapsed_ms = elapsed_ms


class BaseAgent(ABC):
    """Abstract base class for all ZhaoYaoJing agents."""

    name: str = "base"
    prompt_file: str | None = None

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self._system_prompt: str | None = None

    @property
    def system_prompt(self) -> str:
        if self._system_prompt is None and self.prompt_file:
            path = PROMPTS_DIR / self.prompt_file
            self._system_prompt = path.read_text(encoding="utf-8")
        return self._system_prompt or ""

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent with timing and logging."""
        logger.info("Agent [%s] starting", self.name)
        start = time.monotonic()
        try:
            data = await self.run(context)
            elapsed = (time.monotonic() - start) * 1000
            logger.info("Agent [%s] completed in %.0fms", self.name, elapsed)
            return AgentResult(data=data, agent_name=self.name, elapsed_ms=elapsed)
        except Exception:
            elapsed = (time.monotonic() - start) * 1000
            logger.exception("Agent [%s] failed after %.0fms", self.name, elapsed)
            raise

    @abstractmethod
    async def run(self, context: AgentContext) -> dict[str, Any]:
        """Implement agent logic. Returns data dict to merge into context."""
        ...

    async def llm_call(
        self,
        user_content: str,
        system_content: str | None = None,
        response_format: dict | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Helper to make an LLM call with this agent's system prompt."""
        messages = []
        sys_content = system_content or self.system_prompt
        if sys_content:
            messages.append(Message(role="system", content=sys_content))
        messages.append(Message(role="user", content=user_content))

        response = await self.llm_router.complete(
            messages,
            agent_name=self.name,
            temperature=temperature,
            response_format=response_format,
        )
        return strip_code_fences(response.content)
