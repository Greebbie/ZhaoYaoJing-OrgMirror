"""Trigger management API endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.db.database import async_session_factory
from server.notifications.dispatcher import NotificationDispatcher
from server.triggers.event_engine import EventEngine, TriggerEvent
from server.triggers.rules import TriggerRule, load_rules
from server.triggers.scheduler import TriggerScheduler

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Module-level state (initialised at import time with defaults)
# ---------------------------------------------------------------------------

_rules: list[TriggerRule] = []
_engine: EventEngine | None = None
_scheduler: TriggerScheduler | None = None
_dispatcher: NotificationDispatcher | None = None


def _ensure_initialised() -> tuple[list[TriggerRule], EventEngine, TriggerScheduler]:
    """Lazily initialise the trigger subsystem on first API call."""
    global _rules, _engine, _scheduler, _dispatcher  # noqa: PLW0603

    if _engine is None:
        _rules = load_rules()
        _engine = EventEngine(rules=_rules, session_factory=async_session_factory)
        _dispatcher = NotificationDispatcher()
        _scheduler = TriggerScheduler(
            engine=_engine, dispatcher=_dispatcher
        )

    assert _engine is not None
    assert _scheduler is not None
    return _rules, _engine, _scheduler


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TriggerRuleResponse(BaseModel):
    id: str
    type: str
    description_zh: str
    description_en: str
    condition: dict[str, Any]
    action: str
    visibility: str
    enabled: bool


class TriggerRuleListResponse(BaseModel):
    rules: list[TriggerRuleResponse]
    total: int


class TriggerEventResponse(BaseModel):
    rule_id: str
    trigger_type: str
    item_id: str | None
    details: dict[str, Any]
    fired_at: str
    visibility: str


class EvaluateResponse(BaseModel):
    events: list[TriggerEventResponse]
    total: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rule_to_response(rule: TriggerRule) -> TriggerRuleResponse:
    return TriggerRuleResponse(
        id=rule.id,
        type=rule.type,
        description_zh=rule.description_zh,
        description_en=rule.description_en,
        condition=rule.condition,
        action=rule.action,
        visibility=rule.visibility,
        enabled=rule.enabled,
    )


def _event_to_response(event: TriggerEvent) -> TriggerEventResponse:
    return TriggerEventResponse(
        rule_id=event.rule_id,
        trigger_type=event.trigger_type,
        item_id=event.item_id,
        details=event.details,
        fired_at=event.fired_at.isoformat(),
        visibility=event.visibility,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/api/triggers/rules", response_model=TriggerRuleListResponse)
async def list_trigger_rules() -> TriggerRuleListResponse:
    """Return all configured trigger rules."""
    rules, _eng, _sched = _ensure_initialised()
    return TriggerRuleListResponse(
        rules=[_rule_to_response(r) for r in rules],
        total=len(rules),
    )


@router.post("/api/triggers/evaluate", response_model=EvaluateResponse)
async def evaluate_triggers() -> EvaluateResponse:
    """Manually evaluate all enabled trigger rules right now."""
    _rules_list, _eng, scheduler = _ensure_initialised()
    events = await scheduler.run_once()
    return EvaluateResponse(
        events=[_event_to_response(e) for e in events],
        total=len(events),
    )


@router.put("/api/triggers/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str) -> dict[str, Any]:
    """Enable or disable a trigger rule by its ID."""
    rules, engine, _sched = _ensure_initialised()

    target: TriggerRule | None = None
    for rule in rules:
        if rule.id == rule_id:
            target = rule
            break

    if target is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")

    # Create a toggled copy (immutable approach) and replace in the list
    toggled = target.model_copy(update={"enabled": not target.enabled})
    new_rules = [toggled if r.id == rule_id else r for r in rules]

    # Update module-level and engine references
    global _rules  # noqa: PLW0603
    _rules = new_rules
    engine.rules = [r for r in new_rules if r.enabled]

    return {
        "id": toggled.id,
        "enabled": toggled.enabled,
        "message": f"Rule '{rule_id}' is now {'enabled' if toggled.enabled else 'disabled'}",
    }
