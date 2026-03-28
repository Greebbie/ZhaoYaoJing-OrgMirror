import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class EscalationAgent(BaseAgent):
    """Generates objective escalation summaries for stale items."""

    name = "escalation"
    prompt_file = "escalation.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        stale_items = context.get("stale_items", [])

        if not stale_items:
            return {"escalation_items": []}

        monsters = context.get("monsters_detected", [])
        health = context.get("health_score", {})

        summary = json.dumps(
            {
                "stale_items": stale_items,
                "related_monsters": monsters,
                "health_score": health,
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"为以下停滞事项生成升级摘要：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}

        return {
            "escalation_items": parsed.get("escalation_items", []),
        }
