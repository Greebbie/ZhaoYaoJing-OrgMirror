import json
from pathlib import Path
from typing import Any

from server.agents.base import AgentContext, BaseAgent
from server.monsters.codex import monster_codex
from server.schemas.mirror_report import Translation
from server.schemas.monster import MonsterDetected

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class MirrorAgent(BaseAgent):
    name = "mirror"

    async def run(self, context: AgentContext) -> dict[str, Any]:
        content = context["content"]
        language = context.get("language", "zh")

        translations = await self._translate(content, language)
        monsters = await self._detect(content, language)

        return {
            "translations": [t.model_dump() for t in translations],
            "monsters_detected": [m.model_dump() for m in monsters],
        }

    async def _translate(self, text: str, language: str) -> list[Translation]:
        prompt_file = "translate_zh.md" if language != "en" else "translate_en.md"
        prompt_path = PROMPTS_DIR / prompt_file
        system_prompt = prompt_path.read_text(encoding="utf-8")
        codex_context = monster_codex.to_prompt_context(language)
        system_prompt = system_prompt.replace("{codex_context}", codex_context)

        raw = await self.llm_call(
            user_content=text,
            system_content=system_prompt,
        )

        try:
            parsed = json.loads(raw)
            items = parsed if isinstance(parsed, list) else parsed.get("translations", [])
            return [Translation(**item) for item in items]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    async def _detect(self, text: str, language: str) -> list[MonsterDetected]:
        prompt_path = PROMPTS_DIR / "detect.md"
        system_prompt = prompt_path.read_text(encoding="utf-8")
        codex_context = monster_codex.to_prompt_context(language)
        system_prompt = system_prompt.replace("{codex_context}", codex_context)

        raw = await self.llm_call(
            user_content=f"分析以下文本，检测其中的妖怪：\n\n{text}",
            system_content=system_prompt,
        )

        try:
            parsed = json.loads(raw)
            items = parsed if isinstance(parsed, list) else parsed.get("monsters", [])
            return [MonsterDetected(**item) for item in items]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
