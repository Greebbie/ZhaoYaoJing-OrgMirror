import asyncio
import logging
from typing import Any

from server.agents.base import AgentContext, AgentResult, BaseAgent

logger = logging.getLogger(__name__)


class AgentPipeline:
    """Orchestrates agent execution in sequence and parallel."""

    def __init__(self):
        self._steps: list[list[BaseAgent]] = []

    def add_sequential(self, agent: BaseAgent) -> "AgentPipeline":
        """Add an agent to run sequentially."""
        self._steps.append([agent])
        return self

    def add_parallel(self, *agents: BaseAgent) -> "AgentPipeline":
        """Add agents to run in parallel."""
        self._steps.append(list(agents))
        return self

    async def run(self, initial_context: dict[str, Any] | None = None) -> AgentContext:
        """Execute the pipeline, accumulating context."""
        context = AgentContext(initial_context or {})
        results: list[AgentResult] = []

        for step in self._steps:
            if len(step) == 1:
                result = await step[0].execute(context)
                context.update(result.data)
                results.append(result)
            else:
                parallel_results = await asyncio.gather(
                    *(agent.execute(context) for agent in step),
                    return_exceptions=True,
                )
                for r in parallel_results:
                    if isinstance(r, Exception):
                        logger.error("Parallel agent failed: %s", r)
                        continue
                    context.update(r.data)
                    results.append(r)

        context["_pipeline_results"] = results
        return context
