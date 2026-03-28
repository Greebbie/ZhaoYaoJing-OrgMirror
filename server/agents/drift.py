import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class DriftAgent(BaseAgent):
    """Detects silent changes to requirements, owners, goals, and deadlines."""

    name = "drift"
    prompt_file = "drift.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        current_xray = context.get("xray", {})
        previous_xray = context.get("previous_xray", {})

        if not previous_xray:
            return {
                "drifts_detected": [],
                "drift_score": 0.0,
                "drift_summary_zh": "首次分析，无漂移基准",
                "drift_summary_en": "First analysis, no drift baseline",
            }

        summary = json.dumps(
            {
                "current_state": current_xray,
                "previous_state": previous_xray,
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"对比前后状态，检测漂移：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}

        return {
            "drifts_detected": parsed.get("drifts_detected", []),
            "drift_score": parsed.get("drift_score", 0.0),
            "drift_summary_zh": parsed.get("summary_zh", ""),
            "drift_summary_en": parsed.get("summary_en", ""),
        }
