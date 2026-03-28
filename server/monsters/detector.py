import json
import logging
from pathlib import Path

from server.llm.base import Message, strip_code_fences
from server.llm.router import LLMRouter
from server.monsters.codex import MonsterCodex
from server.schemas.monster import MonsterDetected

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_detection_prompt() -> str:
    return (PROMPTS_DIR / "detect.md").read_text(encoding="utf-8")


async def detect_monsters(
    text: str,
    codex: MonsterCodex,
    router: LLMRouter,
) -> list[MonsterDetected]:
    """Use LLM to detect monsters in the given text."""
    codex_context = codex.to_prompt_context("zh")
    system_prompt = _load_detection_prompt().replace(
        "{codex_context}", codex_context
    )

    messages = [
        Message(role="system", content=system_prompt),
        Message(
            role="user",
            content=f"分析以下文本，检测其中的妖怪：\n\n{text}",
        ),
    ]

    response = await router.complete(
        messages,
        agent_name="monster_detector",
    )

    try:
        raw = json.loads(strip_code_fences(response.content))
        # Handle both {"monsters": [...]} and direct array
        items = raw if isinstance(raw, list) else raw.get("monsters", [])
        return [MonsterDetected(**item) for item in items]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error("Failed to parse monster detection response: %s", e)
        return []
