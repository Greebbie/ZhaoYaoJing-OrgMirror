import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent
from server.schemas.mirror_report import Recommendation


class AdvisorAgent(BaseAgent):
    name = "advisor"
    prompt_file = "advisor.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        monsters = context.get("monsters_detected", [])
        translations = context.get("translations", [])
        health = context.get("health_score", {})
        checks = context.get("clarification_checks", [])
        missing = context.get("critical_missing", [])

        summary = json.dumps(
            {
                "monsters_detected": monsters,
                "translations_summary": [
                    {"original": t.get("original", ""), "mirror": t.get("mirror", "")}
                    for t in translations[:10]
                ],
                "health_score": health,
                "critical_missing": missing,
                "clarification_checks": checks[:10],
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"根据以下分析结果生成建议：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
            items = parsed.get("recommendations", [])
            recs = [Recommendation(**item) for item in items]
        except (json.JSONDecodeError, KeyError, TypeError):
            recs = []

        return {"recommendations": [r.model_dump() for r in recs]}
