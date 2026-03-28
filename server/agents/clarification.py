import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class ClarificationAgent(BaseAgent):
    name = "clarification"
    prompt_file = "clarification.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        items = context.get("intake_items", [])
        statements = context.get("intake_statements", [])

        summary = json.dumps(
            {"items": items, "statements": statements},
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"检查以下事项的完整性：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"checks": [], "completeness_score": 0, "critical_missing": []}

        return {
            "clarification_checks": parsed.get("checks", []),
            "completeness_score": parsed.get("completeness_score", 0),
            "critical_missing": parsed.get("critical_missing", []),
        }
