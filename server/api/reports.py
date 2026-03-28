from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.database import get_session
from server.db.models import OrgConfig
from server.db.repositories import OrgConfigRepository, PatternRepository, ReportRepository

router = APIRouter()


class ReportSummary(BaseModel):
    id: str
    content_type: str
    trigger_mode: str
    source: str
    monsters_count: int
    health_score_overall: int | None
    created_at: str


class ReportDetail(BaseModel):
    id: str
    input_text: str
    content_type: str
    trigger_mode: str
    language: str
    source: str
    translations: list
    monsters_detected: list
    xray: dict | None
    health_score: dict | None
    recommendations: list
    created_at: str


class ReportListResponse(BaseModel):
    reports: list[ReportSummary]
    total: int


class WeeklyStats(BaseModel):
    total_analyses: int
    monster_counts: dict[str, int]
    period_start: str
    period_end: str
    top_monsters: list[dict]


class OrgConfigInput(BaseModel):
    name: str = ""
    org_type: str = "startup"
    size: str = "10-30"
    config: dict = {}


@router.get("/api/reports", response_model=ReportListResponse)
async def list_reports(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    repo = ReportRepository(session)
    results = await repo.list_recent(limit=limit, offset=offset)
    total = await repo.count()

    summaries = []
    for r in results:
        health = r.health_score_json or {}
        summaries.append(
            ReportSummary(
                id=r.id,
                content_type=r.content_type,
                trigger_mode=r.trigger_mode,
                source=r.source,
                monsters_count=len(r.monsters_json or []),
                health_score_overall=health.get("overall"),
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
        )

    return ReportListResponse(reports=summaries, total=total)


@router.get("/api/reports/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = ReportRepository(session)
    result = await repo.get_by_id(report_id)
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportDetail(
        id=result.id,
        input_text=result.input_text,
        content_type=result.content_type,
        trigger_mode=result.trigger_mode,
        language=result.language,
        source=result.source,
        translations=result.translations_json or [],
        monsters_detected=result.monsters_json or [],
        xray=result.xray_json,
        health_score=result.health_score_json,
        recommendations=result.recommendations_json or [],
        created_at=result.created_at.isoformat() if result.created_at else "",
    )


@router.post("/api/report/weekly", response_model=WeeklyStats)
async def weekly_report(
    session: AsyncSession = Depends(get_session),
):
    report_repo = ReportRepository(session)
    pattern_repo = PatternRepository(session)

    stats = await report_repo.get_weekly_stats()
    top = await pattern_repo.get_top_monsters(limit=5)

    return WeeklyStats(
        total_analyses=stats["total_analyses"],
        monster_counts=stats["monster_counts"],
        period_start=stats["period_start"],
        period_end=stats["period_end"],
        top_monsters=[
            {
                "monster_id": p.monster_id,
                "count": p.occurrence_count,
                "severity_avg": round(p.severity_avg, 1),
            }
            for p in top
        ],
    )


@router.post("/api/org/config")
async def save_org_config(
    config_input: OrgConfigInput,
    session: AsyncSession = Depends(get_session),
):
    repo = OrgConfigRepository(session)
    org_config = OrgConfig(
        name=config_input.name,
        org_type=config_input.org_type,
        size=config_input.size,
        config_json=config_input.config,
    )
    saved = await repo.save(org_config)
    return {"id": saved.id, "status": "saved"}


@router.get("/api/org/config")
async def get_org_config(
    session: AsyncSession = Depends(get_session),
):
    repo = OrgConfigRepository(session)
    config = await repo.get_latest()
    if not config:
        return {"name": "", "org_type": "startup", "size": "10-30", "config": {}}
    return {
        "id": config.id,
        "name": config.name,
        "org_type": config.org_type,
        "size": config.size,
        "config": config.config_json,
    }
