"""Item tracking API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.database import get_session
from server.db.models import Item
from server.db.repositories import ItemRepository, ReportRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ItemCreateRequest(BaseModel):
    name: str
    description: str | None = None
    status: str = "active"
    org_id: str | None = None


class ItemUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    org_id: str | None = None


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    org_id: str | None
    created_at: str
    updated_at: str


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int


class ItemHistoryEntry(BaseModel):
    id: str
    content_type: str
    trigger_mode: str
    source: str
    monsters_count: int
    created_at: str


class ItemHistoryResponse(BaseModel):
    item_id: str
    history: list[ItemHistoryEntry]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item_to_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        status=item.status,
        org_id=item.org_id,
        created_at=item.created_at.isoformat() if item.created_at else "",
        updated_at=item.updated_at.isoformat() if item.updated_at else "",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/api/items", response_model=ItemResponse, status_code=201)
async def create_item(
    body: ItemCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> ItemResponse:
    """Create a new tracked item."""
    repo = ItemRepository(session)
    item = Item(
        name=body.name,
        description=body.description,
        status=body.status,
        org_id=body.org_id,
    )
    saved = await repo.create(item)
    return _item_to_response(saved)


@router.get("/api/items", response_model=ItemListResponse)
async def list_items(
    limit: int = Query(default=50, le=200),
    org_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ItemListResponse:
    """List all tracked items, ordered by most recently updated."""
    repo = ItemRepository(session)
    items = await repo.list_all(limit=limit, org_id=org_id)
    return ItemListResponse(
        items=[_item_to_response(i) for i in items],
        total=len(items),
    )


@router.get("/api/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    session: AsyncSession = Depends(get_session),
) -> ItemResponse:
    """Retrieve a single item by ID."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


@router.get("/api/items/{item_id}/history", response_model=ItemHistoryResponse)
async def get_item_history(
    item_id: str,
    session: AsyncSession = Depends(get_session),
) -> ItemHistoryResponse:
    """Get the mirror-analysis history for a tracked item."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    report_repo = ReportRepository(session)
    results = await report_repo.get_by_item_id(item_id)

    entries = [
        ItemHistoryEntry(
            id=r.id,
            content_type=r.content_type,
            trigger_mode=r.trigger_mode,
            source=r.source,
            monsters_count=len(r.monsters_json or []),
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in results
    ]
    return ItemHistoryResponse(item_id=item_id, history=entries)


@router.patch("/api/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    body: ItemUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> ItemResponse:
    """Update an item's fields (name, description, status, org_id)."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if body.name is not None:
        item.name = body.name
    if body.description is not None:
        item.description = body.description
    if body.status is not None:
        item.status = body.status
    if body.org_id is not None:
        item.org_id = body.org_id

    await session.commit()
    await session.refresh(item)
    return _item_to_response(item)
