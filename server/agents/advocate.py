import json
from pathlib import Path
from typing import Any

from server.agents.base import AgentContext, BaseAgent

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class AdvocateAgent(BaseAgent):
    """Represents one stakeholder party in a deliberation."""

    name = "advocate"

    def __init__(self, llm_router, party_description: str):
        super().__init__(llm_router)
        self.party_description = party_description

    async def run(self, context: AgentContext) -> dict[str, Any]:
        prompt_template = (PROMPTS_DIR / "advocate.md").read_text(encoding="utf-8")
        system_prompt = prompt_template.replace(
            "{party_description}", self.party_description
        )

        content = context.get("content", "")
        translations = context.get("translations", [])
        summary = json.dumps(
            {
                "original_text": content[:2000],
                "key_translations": translations[:5],
            },
            ensure_ascii=False,
        )

        raw = await self.llm_call(
            user_content=f"根据以下讨论内容，代表你的角色表态：\n\n{summary}",
            system_content=system_prompt,
        )

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "party": self.party_description,
                "position": "conditional",
                "position_statement": "无法解析立场",
                "core_constraints": [],
                "minimum_acceptable_outcome": "",
                "alternative_proposal": "",
                "key_concerns": [],
            }


class CrossExaminationAgent(BaseAgent):
    """Handles round 2: cross-examination between advocates."""

    name = "cross_examination"

    def __init__(self, llm_router, party_description: str):
        super().__init__(llm_router)
        self.party_description = party_description

    async def run_with_positions(
        self, context: AgentContext, other_positions: list[dict]
    ) -> dict[str, Any]:
        prompt_template = (PROMPTS_DIR / "cross_examination.md").read_text(
            encoding="utf-8"
        )
        system_prompt = prompt_template.replace(
            "{party_description}", self.party_description
        ).replace(
            "{other_positions}",
            json.dumps(other_positions, ensure_ascii=False),
        )

        raw = await self.llm_call(
            user_content="审视其他方的立场，进行交叉质询。",
            system_content=system_prompt,
        )

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "party": self.party_description,
                "contradictions_found": [],
                "questions": [],
                "position_revised": False,
                "revised_position": None,
            }

    async def run(self, context: AgentContext) -> dict[str, Any]:
        other_positions = context.get("other_positions", [])
        return await self.run_with_positions(context, other_positions)
