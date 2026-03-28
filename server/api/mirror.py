import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.agents.advisor import AdvisorAgent
from server.agents.clarification import ClarificationAgent
from server.agents.health import HealthAgent
from server.agents.intake import IntakeAgent
from server.agents.mirror import MirrorAgent
from server.agents.pipeline import AgentPipeline
from server.db.database import get_session
from server.db.models import MirrorResult
from server.db.repositories import PatternRepository, ReportRepository
from server.llm.base import LLMError
from server.llm.router import llm_router
from server.schemas.mirror_input import MirrorInput
from server.schemas.mirror_report import (
    HealthDimensions,
    HealthScore,
    MirrorReport,
    Recommendation,
    Translation,
)
from server.schemas.monster import MonsterDetected

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_pipeline() -> AgentPipeline:
    """Build the standard analysis pipeline."""
    pipeline = AgentPipeline()
    pipeline.add_sequential(IntakeAgent(llm_router))
    pipeline.add_sequential(ClarificationAgent(llm_router))
    pipeline.add_sequential(MirrorAgent(llm_router))
    pipeline.add_parallel(HealthAgent(llm_router), AdvisorAgent(llm_router))
    return pipeline


@router.post("/api/mirror", response_model=MirrorReport)
async def mirror_analyze(
    input_data: MirrorInput,
    session: AsyncSession | None = Depends(get_session),
):
    """Analyze text through the full agent pipeline."""
    if not input_data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    language = input_data.language if input_data.language != "auto" else "zh"

    initial_context = {
        "content": input_data.content,
        "content_type": input_data.content_type,
        "language": language,
        "trigger_mode": input_data.trigger_mode,
        "anonymous_mode": input_data.anonymous_mode,
    }

    try:
        pipeline = _build_pipeline()
        context = await pipeline.run(initial_context)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM service error: {e}")

    # Build report from pipeline context
    translations_data = context.get("translations", [])
    monsters_data = context.get("monsters_detected", [])
    recommendations_data = context.get("recommendations", [])
    health_data = context.get("health_score")

    translations = [Translation(**t) for t in translations_data]
    monsters = [MonsterDetected(**m) for m in monsters_data]
    recommendations = [Recommendation(**r) for r in recommendations_data]

    health_score = None
    if health_data:
        dims = health_data.get("dimensions", {})
        health_score = HealthScore(
            overall=health_data.get("overall", 50),
            dimensions=HealthDimensions(
                clarity=dims.get("clarity", 50),
                accountability=dims.get("accountability", 50),
                momentum=dims.get("momentum", 50),
                trust=dims.get("trust", 50),
            ),
        )

    # Persist to database
    if session:
        try:
            report_repo = ReportRepository(session)
            db_result = MirrorResult(
                input_text=input_data.content,
                content_type=input_data.content_type,
                trigger_mode=input_data.trigger_mode,
                language=language,
                translations_json=translations_data,
                monsters_json=monsters_data,
                health_score_json=health_data,
                recommendations_json=recommendations_data,
                source="web",
            )
            await report_repo.create(db_result)

            # Update pattern memory
            pattern_repo = PatternRepository(session)
            for m in monsters_data:
                await pattern_repo.upsert(
                    monster_id=m.get("monster_id", "unknown"),
                    severity=float(m.get("severity", 1)),
                )
        except Exception:
            logger.exception("Failed to persist mirror result")

    return MirrorReport(
        translations=translations,
        monsters_detected=monsters,
        health_score=health_score,
        recommendations=recommendations,
    )
