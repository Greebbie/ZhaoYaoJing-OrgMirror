import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.database import get_session
from server.db.models import Member, MemberPattern, MirrorResult

logger = logging.getLogger(__name__)
router = APIRouter()


class MemberInput(BaseModel):
    display_name: str
    role: str | None = None
    department: str | None = None
    authority_level: str = "IC"


class MemberResponse(BaseModel):
    id: str
    display_name: str
    role: str | None
    department: str | None
    authority_level: str
    created_at: str


class MemberPatternResponse(BaseModel):
    monster_id: str
    occurrence_count: int
    severity_avg: float
    last_seen: str


@router.get("/api/members")
async def list_members(session: AsyncSession = Depends(get_session)):
    stmt = select(Member).order_by(Member.display_name)
    result = await session.execute(stmt)
    members = result.scalars().all()
    return {
        "members": [
            MemberResponse(
                id=m.id,
                display_name=m.display_name,
                role=m.role,
                department=m.department,
                authority_level=m.authority_level,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
            for m in members
        ]
    }


@router.post("/api/members")
async def create_member(
    data: MemberInput,
    session: AsyncSession = Depends(get_session),
):
    member = Member(
        display_name=data.display_name,
        role=data.role,
        department=data.department,
        authority_level=data.authority_level,
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return MemberResponse(
        id=member.id,
        display_name=member.display_name,
        role=member.role,
        department=member.department,
        authority_level=member.authority_level,
        created_at=member.created_at.isoformat() if member.created_at else "",
    )


@router.patch("/api/members/{member_id}")
async def update_member(
    member_id: str,
    data: MemberInput,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Member).where(Member.id == member_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.display_name = data.display_name
    member.role = data.role
    member.department = data.department
    member.authority_level = data.authority_level
    await session.commit()
    await session.refresh(member)
    return MemberResponse(
        id=member.id,
        display_name=member.display_name,
        role=member.role,
        department=member.department,
        authority_level=member.authority_level,
        created_at=member.created_at.isoformat() if member.created_at else "",
    )


@router.delete("/api/members/{member_id}")
async def delete_member(
    member_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Member).where(Member.id == member_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Member not found")

    await session.execute(delete(Member).where(Member.id == member_id))
    await session.commit()
    return {"status": "deleted"}


@router.get("/api/members/{member_id}/patterns")
async def member_patterns(
    member_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get per-person monster pattern frequency."""
    # Check member exists
    member_result = await session.execute(
        select(Member).where(Member.id == member_id)
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    stmt = (
        select(MemberPattern)
        .where(MemberPattern.member_id == member_id)
        .order_by(desc(MemberPattern.occurrence_count))
    )
    result = await session.execute(stmt)
    patterns = result.scalars().all()

    return {
        "member": {
            "id": member.id,
            "display_name": member.display_name,
        },
        "patterns": [
            MemberPatternResponse(
                monster_id=p.monster_id,
                occurrence_count=p.occurrence_count,
                severity_avg=round(p.severity_avg, 1),
                last_seen=p.last_seen.isoformat() if p.last_seen else "",
            )
            for p in patterns
        ],
    }


@router.get("/api/members/{member_id}/history")
async def member_history(
    member_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get analysis history linked to this member."""
    stmt = (
        select(MirrorResult)
        .where(MirrorResult.member_id == member_id)
        .order_by(desc(MirrorResult.created_at))
        .limit(20)
    )
    result = await session.execute(stmt)
    results = result.scalars().all()

    return {
        "analyses": [
            {
                "id": r.id,
                "content_type": r.content_type,
                "monsters_count": len(r.monsters_json or []),
                "health_score": (r.health_score_json or {}).get("overall"),
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in results
        ]
    }
