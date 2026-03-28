"""Event trigger engine that evaluates rules against live data."""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from server.db.models import Item, MirrorResult, PatternMemory
from server.triggers.rules import TriggerRule

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TriggerEvent:
    """Immutable record of a fired trigger."""

    rule_id: str
    trigger_type: str
    item_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    fired_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    visibility: str = "thread"


class EventEngine:
    """Evaluates trigger rules against the current database state.

    Args:
        rules: Loaded trigger rules (only enabled rules are kept).
        session_factory: SQLAlchemy async session maker.
    """

    def __init__(
        self,
        rules: list[TriggerRule],
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.rules = [r for r in rules if r.enabled]
        self.session_factory = session_factory

    async def evaluate_all(self) -> list[TriggerEvent]:
        """Evaluate every enabled rule and return all fired events."""
        events: list[TriggerEvent] = []
        async with self.session_factory() as session:
            for rule in self.rules:
                try:
                    fired = await self._evaluate_rule(rule, session)
                    events.extend(fired)
                except Exception:
                    logger.exception("Error evaluating rule %s", rule.id)
        return events

    async def _evaluate_rule(
        self, rule: TriggerRule, session: AsyncSession
    ) -> list[TriggerEvent]:
        """Dispatch evaluation to the handler matching ``rule.type``."""
        handler = _RULE_HANDLERS.get(rule.type)
        if handler is None:
            logger.warning("No handler registered for rule type: %s", rule.type)
            return []
        return await handler(rule, session)


# ---------------------------------------------------------------------------
# Per-type evaluation helpers
# ---------------------------------------------------------------------------

async def _evaluate_stale_item(
    rule: TriggerRule, session: AsyncSession
) -> list[TriggerEvent]:
    """Find items that have not been updated within the configured window."""
    days = rule.condition.get("days_since_last_update", 7)
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)

    stmt = select(Item).where(
        Item.status == "active",
        Item.updated_at < cutoff,
    )
    result = await session.execute(stmt)
    stale_items = list(result.scalars().all())

    return [
        TriggerEvent(
            rule_id=rule.id,
            trigger_type=rule.type,
            item_id=item.id,
            details={
                "item_name": item.name,
                "last_updated": item.updated_at.isoformat() if item.updated_at else "",
                "days_stale": days,
                "action": rule.action,
            },
            visibility=rule.visibility,
        )
        for item in stale_items
    ]


async def _evaluate_meeting_repeat(
    rule: TriggerRule, session: AsyncSession
) -> list[TriggerEvent]:
    """Flag pattern-memory monsters that exceed the repeat threshold."""
    threshold = rule.condition.get("repeat_threshold", 3)

    stmt = select(PatternMemory).where(
        PatternMemory.occurrence_count >= threshold,
    )
    result = await session.execute(stmt)
    patterns = list(result.scalars().all())

    return [
        TriggerEvent(
            rule_id=rule.id,
            trigger_type=rule.type,
            details={
                "monster_id": p.monster_id,
                "occurrence_count": p.occurrence_count,
                "severity_avg": round(p.severity_avg, 2),
                "action": rule.action,
            },
            visibility=rule.visibility,
        )
        for p in patterns
    ]


async def _evaluate_commitment_no_followup(
    rule: TriggerRule, session: AsyncSession
) -> list[TriggerEvent]:
    """Find items with a 'commitment' content type that have had no recent results."""
    hours = rule.condition.get("hours_since_commitment", 72)
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=hours)

    stmt = select(MirrorResult).where(
        MirrorResult.content_type == "commitment",
        MirrorResult.created_at < cutoff,
    )
    result = await session.execute(stmt)
    commitments = list(result.scalars().all())

    events: list[TriggerEvent] = []
    for c in commitments:
        # Check whether a follow-up result exists after this commitment
        followup_stmt = select(MirrorResult.id).where(
            MirrorResult.item_id == c.item_id,
            MirrorResult.created_at > c.created_at,
        )
        followup = await session.execute(followup_stmt)
        if followup.scalar_one_or_none() is None:
            events.append(
                TriggerEvent(
                    rule_id=rule.id,
                    trigger_type=rule.type,
                    item_id=c.item_id,
                    details={
                        "commitment_id": c.id,
                        "created_at": c.created_at.isoformat() if c.created_at else "",
                        "hours_overdue": hours,
                        "action": rule.action,
                    },
                    visibility=rule.visibility,
                )
            )
    return events


async def _evaluate_owner_silence(
    rule: TriggerRule, session: AsyncSession
) -> list[TriggerEvent]:
    """Flag items whose owner has not produced any mirror result recently."""
    days = rule.condition.get("days_since_owner_activity", 5)
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)

    stmt = select(Item).where(Item.status == "active")
    result = await session.execute(stmt)
    active_items = list(result.scalars().all())

    events: list[TriggerEvent] = []
    for item in active_items:
        # Look for any recent mirror result linked to this item
        activity_stmt = select(MirrorResult.id).where(
            MirrorResult.item_id == item.id,
            MirrorResult.created_at >= cutoff,
        )
        activity = await session.execute(activity_stmt)
        if activity.scalar_one_or_none() is None:
            events.append(
                TriggerEvent(
                    rule_id=rule.id,
                    trigger_type=rule.type,
                    item_id=item.id,
                    details={
                        "item_name": item.name,
                        "days_silent": days,
                        "action": rule.action,
                    },
                    visibility=rule.visibility,
                )
            )
    return events


async def _evaluate_new_requirement(
    rule: TriggerRule, session: AsyncSession
) -> list[TriggerEvent]:
    """Flag recent requirement items that have no X-ray result yet."""
    one_day_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)

    stmt = select(Item).where(
        Item.status == "active",
        Item.created_at >= one_day_ago,
    )
    result = await session.execute(stmt)
    new_items = list(result.scalars().all())

    events: list[TriggerEvent] = []
    for item in new_items:
        # Check if an X-ray result already exists for this item
        xray_stmt = select(MirrorResult.id).where(
            MirrorResult.item_id == item.id,
            MirrorResult.xray_json.isnot(None),
        )
        xray = await session.execute(xray_stmt)
        if xray.scalar_one_or_none() is None:
            events.append(
                TriggerEvent(
                    rule_id=rule.id,
                    trigger_type=rule.type,
                    item_id=item.id,
                    details={
                        "item_name": item.name,
                        "action": rule.action,
                    },
                    visibility=rule.visibility,
                )
            )
    return events


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

_RULE_HANDLERS: dict[str, Any] = {
    "stale_item": _evaluate_stale_item,
    "meeting_repeat": _evaluate_meeting_repeat,
    "commitment_no_followup": _evaluate_commitment_no_followup,
    "owner_silence": _evaluate_owner_silence,
    "new_requirement": _evaluate_new_requirement,
}
