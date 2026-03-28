import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class IntakeAgent(BaseAgent):
    name = "intake"
    prompt_file = "intake.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        content = context["content"]
        anonymous = context.get("anonymous_mode", True)

        prompt_extra = ""
        if anonymous:
            prompt_extra = "\n\nanonymous_mode = true，请将所有人名替换为角色A/角色B/角色C。"

        raw = await self.llm_call(
            user_content=f"解析以下文本：{prompt_extra}\n\n{content}",
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"statements": [], "items": [], "people": []}

        return {
            "intake_statements": parsed.get("statements", []),
            "intake_items": parsed.get("items", []),
            "intake_people": parsed.get("people", []),
        }
