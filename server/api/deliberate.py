import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.agents.base import AgentContext
from server.agents.deliberation import run_deliberation
from server.llm.base import LLMError
from server.llm.router import llm_router

logger = logging.getLogger(__name__)
router = APIRouter()


class DeliberationInput(BaseModel):
    content: str
    parties: list[str]  # List of party descriptions
    language: str = "zh"
    context: dict | None = None  # Optional prior analysis context


class DeliberationResult(BaseModel):
    deliberation: dict
    rounds_completed: int
    parties_count: int
    advocate_positions: list[dict]
    cross_examinations: list[dict]


@router.post("/api/deliberate", response_model=DeliberationResult)
async def deliberate(input_data: DeliberationInput):
    """Trigger multi-party deliberation."""
    if not input_data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    if len(input_data.parties) < 2:
        raise HTTPException(
            status_code=400, detail="Need at least 2 parties for deliberation"
        )
    if len(input_data.parties) > 5:
        raise HTTPException(
            status_code=400, detail="Maximum 5 parties allowed"
        )

    context = AgentContext({
        "content": input_data.content,
        "language": input_data.language,
        **(input_data.context or {}),
    })

    try:
        result = await run_deliberation(
            context=context,
            parties=input_data.parties,
            router=llm_router,
        )
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM service error: {e}")

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return DeliberationResult(**result)
