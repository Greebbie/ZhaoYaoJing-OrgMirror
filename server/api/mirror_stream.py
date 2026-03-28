import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from server.agents.advisor import AdvisorAgent
from server.agents.base import AgentContext
from server.agents.health import HealthAgent
from server.agents.mirror import MirrorAgent
from server.llm.base import LLMError
from server.llm.router import llm_router
from server.schemas.mirror_input import MirrorInput

logger = logging.getLogger(__name__)
router = APIRouter()


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _run_stream(input_data: MirrorInput) -> AsyncGenerator[str, None]:
    """
    Optimized pipeline: Mirror → [Health + Advisor] in parallel.
    Skips Intake + Clarification to cut ~60s off total time.
    Results stream to frontend as each step completes.
    """
    language = input_data.language if input_data.language != "auto" else "zh"
    context = AgentContext({
        "content": input_data.content,
        "content_type": input_data.content_type,
        "language": language,
        "trigger_mode": input_data.trigger_mode,
        "anonymous_mode": input_data.anonymous_mode,
    })

    # Step 1: Mirror — translation + detection (the core value, ~30s)
    yield _sse("status", {"step": "mirror", "message": "照妖翻译 + 妖怪检测..."})
    try:
        mirror = MirrorAgent(llm_router)
        result = await mirror.execute(context)
        context.update(result.data)
        yield _sse("mirror", {
            "elapsed_ms": result.elapsed_ms,
            "translations": result.data.get("translations", []),
            "monsters_detected": result.data.get("monsters_detected", []),
        })
    except LLMError as e:
        yield _sse("error", {"step": "mirror", "message": str(e)})
        yield _sse("complete", {"translations": [], "monsters_detected": []})
        return

    # Step 2: Health + Advisor in parallel (~20s, runs while user reads translations)
    yield _sse("status", {"step": "scoring", "message": "评分 + 生成建议..."})
    try:
        health_result, advisor_result = await asyncio.gather(
            HealthAgent(llm_router).execute(context),
            AdvisorAgent(llm_router).execute(context),
            return_exceptions=True,
        )

        if not isinstance(health_result, Exception):
            context.update(health_result.data)
            yield _sse("health", {
                "elapsed_ms": health_result.elapsed_ms,
                "health_score": health_result.data.get("health_score", {}),
            })

        if not isinstance(advisor_result, Exception):
            context.update(advisor_result.data)
            yield _sse("recommendations", {
                "elapsed_ms": advisor_result.elapsed_ms,
                "recommendations": advisor_result.data.get("recommendations", []),
            })
    except LLMError as e:
        yield _sse("error", {"step": "scoring", "message": str(e)})

    yield _sse("complete", {
        "translations": context.get("translations", []),
        "monsters_detected": context.get("monsters_detected", []),
        "health_score": context.get("health_score"),
        "recommendations": context.get("recommendations", []),
    })


@router.post("/api/mirror/stream")
async def mirror_stream(input_data: MirrorInput):
    """SSE streaming mirror analysis — results arrive as each agent completes."""
    if not input_data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    return StreamingResponse(
        _run_stream(input_data),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
