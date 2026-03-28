import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class ArbiterAgent(BaseAgent):
    """Convergence engine that synthesizes all advocate positions into option packages."""

    name = "arbiter"
    prompt_file = "arbiter.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        advocate_positions = context.get("advocate_positions", [])
        cross_examinations = context.get("cross_examinations", [])

        summary = json.dumps(
            {
                "advocate_positions": advocate_positions,
                "cross_examinations": cross_examinations,
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"综合以下各方立场，生成方案包：\n\n{summary}",
        )

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "conflict_type": "unknown",
                "parties_summary": [],
                "options": [],
                "unresolved": ["无法解析仲裁结果"],
                "recommended_option": None,
                "escalation_recommendation": None,
            }

        return {"deliberation": result}
