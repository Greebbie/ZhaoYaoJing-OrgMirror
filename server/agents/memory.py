import json
from typing import Any

from server.agents.base import AgentContext, BaseAgent


class MemoryAgent(BaseAgent):
    """Tracks historical patterns, identifies recurring dysfunction across items and time."""

    name = "memory"
    prompt_file = "memory.md"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        monsters = context.get("monsters_detected", [])
        pattern_history = context.get("pattern_history", [])

        if not monsters:
            return {
                "memory_patterns": [],
                "history_summary_zh": "无历史模式数据",
                "history_summary_en": "No historical pattern data",
            }

        summary = json.dumps(
            {
                "current_monsters": monsters,
                "pattern_history": pattern_history,
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"分析跨时间的模式：\n\n{summary}",
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}

        return {
            "memory_patterns": parsed.get("recurring_patterns", []),
            "history_summary_zh": parsed.get("history_summary_zh", ""),
            "history_summary_en": parsed.get("history_summary_en", ""),
        }
