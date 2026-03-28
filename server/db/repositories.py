import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.models import Item, MirrorResult, OrgConfig, PatternMemory


class ReportRepository:
    """CRUD operations for mirror results."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, result: MirrorResult) -> MirrorResult:
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def get_by_id(self, result_id: str) -> MirrorResult | None:
        stmt = select(MirrorResult).where(MirrorResult.id == result_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_recent(
        self, limit: int = 20, offset: int = 0, org_id: str | None = None
    ) -> list[MirrorResult]:
        stmt = (
            select(MirrorResult)
            .order_by(desc(MirrorResult.created_at))
            .limit(limit)
            .offset(offset)
        )
        if org_id:
            stmt = stmt.where(MirrorResult.org_id == org_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, org_id: str | None = None) -> int:
        stmt = select(func.count(MirrorResult.id))
        if org_id:
            stmt = stmt.where(MirrorResult.org_id == org_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_item_id(
        self, item_id: str, limit: int = 50
    ) -> list[MirrorResult]:
        """Return mirror results linked to a specific item, newest first."""
        stmt = (
            select(MirrorResult)
            .where(MirrorResult.item_id == item_id)
            .order_by(desc(MirrorResult.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_weekly_stats(
        self, org_id: str | None = None
    ) -> dict:
        """Get aggregated stats for the past 7 days."""
        week_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
        stmt = select(MirrorResult).where(MirrorResult.created_at >= week_ago)
        if org_id:
            stmt = stmt.where(MirrorResult.org_id == org_id)
        result = await self.session.execute(stmt)
        results = list(result.scalars().all())

        # Aggregate monster counts
        monster_counts: dict[str, int] = {}
        for r in results:
            for m in r.monsters_json or []:
                mid = m.get("monster_id", "unknown")
                monster_counts[mid] = monster_counts.get(mid, 0) + 1

        return {
            "total_analyses": len(results),
            "monster_counts": monster_counts,
            "period_start": week_ago.isoformat(),
            "period_end": datetime.datetime.now(datetime.UTC).isoformat(),
        }


class ItemRepository:
    """CRUD operations for tracked items."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, item: Item) -> Item:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: str) -> Item | None:
        stmt = select(Item).where(Item.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self, limit: int = 50, org_id: str | None = None
    ) -> list[Item]:
        stmt = select(Item).order_by(desc(Item.updated_at)).limit(limit)
        if org_id:
            stmt = stmt.where(Item.org_id == org_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PatternRepository:
    """CRUD operations for pattern memory."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, monster_id: str, severity: float, org_id: str | None = None):
        """Increment count or create new pattern record."""
        stmt = select(PatternMemory).where(
            PatternMemory.monster_id == monster_id,
            PatternMemory.org_id == org_id,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.occurrence_count += 1
            n = existing.occurrence_count
            existing.severity_avg = (
                (existing.severity_avg * (n - 1) + severity) / n
            )
            existing.last_seen = datetime.datetime.now(datetime.UTC)
        else:
            pattern = PatternMemory(
                monster_id=monster_id,
                occurrence_count=1,
                severity_avg=severity,
                org_id=org_id,
            )
            self.session.add(pattern)

        await self.session.commit()

    async def get_top_monsters(
        self, limit: int = 10, org_id: str | None = None
    ) -> list[PatternMemory]:
        stmt = (
            select(PatternMemory)
            .order_by(desc(PatternMemory.occurrence_count))
            .limit(limit)
        )
        if org_id:
            stmt = stmt.where(PatternMemory.org_id == org_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class OrgConfigRepository:
    """CRUD operations for org configuration."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, config: OrgConfig) -> OrgConfig:
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def get_latest(self) -> OrgConfig | None:
        stmt = select(OrgConfig).order_by(desc(OrgConfig.updated_at)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
