import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.llm.base import LLMError, Message, strip_code_fences
from server.llm.router import llm_router
from server.schemas.mirror_report import XRay

logger = logging.getLogger(__name__)
router = APIRouter()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class XRayInput(BaseModel):
    content: str
    content_type: str = "requirement_doc"


@router.post("/api/xray", response_model=XRay)
async def generate_xray(input_data: XRayInput):
    """Generate an X-ray card for a requirement or item."""
    if not input_data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    system_prompt = (PROMPTS_DIR / "xray.md").read_text(encoding="utf-8")

    messages = [
        Message(role="system", content=system_prompt),
        Message(
            role="user",
            content=f"为以下内容生成 X 光片：\n\n{input_data.content}",
        ),
    ]

    try:
        response = await llm_router.complete(
            messages,
            agent_name="xray_generator",
        )
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM service error: {e}")

    try:
        parsed = json.loads(strip_code_fences(response.content))
        return XRay(
            objective=parsed.get("objective", "unclear"),
            deadline=parsed.get("deadline", "unspecified"),
            owner=parsed.get("owner", "unassigned"),
            dependencies=parsed.get("dependencies", []),
            success_criteria=parsed.get("success_criteria", "undefined"),
            missing_info=parsed.get("missing_info", []),
            blockers=parsed.get("blockers", []),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error("Failed to parse xray response: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate X-ray")
