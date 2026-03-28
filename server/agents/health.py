import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent
from server.schemas.mirror_report import HealthDimensions, HealthScore


class HealthAgent(BaseAgent):
    name = "health"
    prompt_file = "health_score.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        monsters = context.get("monsters_detected", [])
        translations = context.get("translations", [])
        checks = context.get("clarification_checks", [])

        summary = json.dumps(
            {
                "monsters_detected": monsters,
                "translations_count": len(translations),
                "clarification_checks": checks,
                "completeness_score": context.get("completeness_score", 0),
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"根据以下分析结果评分：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
            dims = parsed.get("dimensions", {})
            score = HealthScore(
                overall=parsed.get("overall", 50),
                dimensions=HealthDimensions(
                    clarity=dims.get("clarity", 50),
                    accountability=dims.get("accountability", 50),
                    momentum=dims.get("momentum", 50),
                    trust=dims.get("trust", 50),
                ),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            score = HealthScore(
                overall=50,
                dimensions=HealthDimensions(
                    clarity=50, accountability=50, momentum=50, trust=50
                ),
            )

        return {"health_score": score.model_dump()}
