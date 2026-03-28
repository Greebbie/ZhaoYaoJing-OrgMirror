import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.database import get_session
from server.db.models import Item, MirrorResult, PatternMemory

router = APIRouter()


def _days_since(dt: datetime.datetime | None) -> int:
    if not dt:
        return 0
    now = datetime.datetime.now(datetime.UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)
    return max(0, (now - dt).days)


class DashboardSummary(BaseModel):
    health_score_avg: float | None
    total_analyses: int
    total_items: int
    monster_counts: dict[str, int]
    top_monsters: list[dict]
    risk_items: list[dict]
    period: str


class HealthHistoryPoint(BaseModel):
    date: str
    overall: int


class MonsterStat(BaseModel):
    monster_id: str
    count: int
    severity_avg: float


@router.get("/api/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(
    days: int = 7,
    session: AsyncSession = Depends(get_session),
):
    """Get aggregated dashboard data."""
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)

    # Total analyses in period
    count_stmt = select(func.count(MirrorResult.id)).where(
        MirrorResult.created_at >= cutoff
    )
    total = (await session.execute(count_stmt)).scalar_one()

    # Total items
    items_count = (await session.execute(select(func.count(Item.id)))).scalar_one()

    # Average health score
    results_stmt = select(MirrorResult).where(MirrorResult.created_at >= cutoff)
    results = (await session.execute(results_stmt)).scalars().all()

    health_scores = []
    monster_counts: dict[str, int] = {}
    for r in results:
        if r.health_score_json:
            overall = r.health_score_json.get("overall")
            if overall is not None:
                health_scores.append(overall)
        for m in r.monsters_json or []:
            mid = m.get("monster_id", "unknown")
            monster_counts[mid] = monster_counts.get(mid, 0) + 1

    avg_health = sum(health_scores) / len(health_scores) if health_scores else None

    # Top monsters from pattern memory
    top_stmt = (
        select(PatternMemory)
        .order_by(desc(PatternMemory.occurrence_count))
        .limit(10)
    )
    top_patterns = (await session.execute(top_stmt)).scalars().all()
    top_monsters = [
        {
            "monster_id": p.monster_id,
            "count": p.occurrence_count,
            "severity_avg": round(p.severity_avg, 1),
        }
        for p in top_patterns
    ]

    # Risk items (stale or high-monster-count)
    stale_cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
    stale_stmt = (
        select(Item)
        .where(Item.updated_at < stale_cutoff, Item.status == "active")
        .limit(10)
    )
    stale_items = (await session.execute(stale_stmt)).scalars().all()
    risk_items = [
        {
            "id": item.id,
            "name": item.name,
            "status": item.status,
            "days_stale": _days_since(item.updated_at),
        }
        for item in stale_items
    ]

    return DashboardSummary(
        health_score_avg=round(avg_health, 1) if avg_health else None,
        total_analyses=total,
        total_items=items_count,
        monster_counts=monster_counts,
        top_monsters=top_monsters,
        risk_items=risk_items,
        period=f"{days}d",
    )


@router.get("/api/dashboard/health-history", response_model=list[HealthHistoryPoint])
async def health_history(
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """Get health score time series."""
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)
    stmt = (
        select(MirrorResult)
        .where(MirrorResult.created_at >= cutoff)
        .order_by(MirrorResult.created_at)
    )
    results = (await session.execute(stmt)).scalars().all()

    points = []
    for r in results:
        if r.health_score_json and r.created_at:
            overall = r.health_score_json.get("overall")
            if overall is not None:
                points.append(
                    HealthHistoryPoint(
                        date=r.created_at.isoformat(),
                        overall=overall,
                    )
                )
    return points


@router.get("/api/dashboard/monster-stats", response_model=list[MonsterStat])
async def monster_stats(
    session: AsyncSession = Depends(get_session),
):
    """Get monster frequency and severity data."""
    stmt = select(PatternMemory).order_by(desc(PatternMemory.occurrence_count))
    patterns = (await session.execute(stmt)).scalars().all()
    return [
        MonsterStat(
            monster_id=p.monster_id,
            count=p.occurrence_count,
            severity_avg=round(p.severity_avg, 1),
        )
        for p in patterns
    ]
