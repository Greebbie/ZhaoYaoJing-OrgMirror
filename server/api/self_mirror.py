import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.llm.base import LLMError, Message, strip_code_fences
from server.llm.router import llm_router

logger = logging.getLogger(__name__)
router = APIRouter()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class SelfMirrorInput(BaseModel):
    content: str
    language: str = "auto"


class PatternDetected(BaseModel):
    monster_id: str
    text_segment: str
    issue_zh: str
    issue_en: str


class SelfMirrorResult(BaseModel):
    patterns_detected: list[PatternDetected]
    suggested_rewrite: str
    improvement_notes_zh: str
    improvement_notes_en: str


@router.post("/api/self-mirror", response_model=SelfMirrorResult)
async def self_mirror(input_data: SelfMirrorInput):
    """Analyze your own draft message before sending."""
    if not input_data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    system_prompt = (PROMPTS_DIR / "self_mirror.md").read_text(encoding="utf-8")

    messages = [
        Message(role="system", content=system_prompt),
        Message(
            role="user",
            content=f"请检查我准备发送的这段话：\n\n{input_data.content}",
        ),
    ]

    try:
        response = await llm_router.complete(
            messages,
            agent_name="self_mirror",
        )
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM service error: {e}")

    try:
        parsed = json.loads(strip_code_fences(response.content))
        return SelfMirrorResult(
            patterns_detected=[
                PatternDetected(**p) for p in parsed.get("patterns_detected", [])
            ],
            suggested_rewrite=parsed.get("suggested_rewrite", input_data.content),
            improvement_notes_zh=parsed.get("improvement_notes_zh", ""),
            improvement_notes_en=parsed.get("improvement_notes_en", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error("Failed to parse self-mirror response: %s", e)
        return SelfMirrorResult(
            patterns_detected=[],
            suggested_rewrite=input_data.content,
            improvement_notes_zh="分析失败，请重试",
            improvement_notes_en="Analysis failed, please retry",
        )
