import datetime
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class Item(Base):
    """A tracked organizational item/topic."""

    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | resolved | stale
    org_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class MirrorResult(Base):
    """Stored mirror analysis result."""

    __tablename__ = "mirror_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    input_text: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50))
    trigger_mode: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(10), default="zh")
    translations_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    monsters_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    xray_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    health_score_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendations_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    item_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    org_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(20), default="web")  # web | feishu | wecom | slack
    member_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class PatternMemory(Base):
    """Aggregated pattern occurrence data."""

    __tablename__ = "pattern_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    monster_id: Mapped[str] = mapped_column(String(100), index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    severity_avg: Mapped[float] = mapped_column(Float, default=1.0)
    last_seen: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    org_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    context_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class OrgConfig(Base):
    """Stored organization configuration."""

    __tablename__ = "org_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), default="")
    org_type: Mapped[str] = mapped_column(String(50), default="startup")
    size: Mapped[str] = mapped_column(String(20), default="10-30")
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Member(Base):
    """Team member profile (non-sensitive only)."""

    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    authority_level: Mapped[str] = mapped_column(
        String(20), default="IC"
    )  # IC | TL | Manager | Director | VP
    org_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class BotConnection(Base):
    """Bot platform connection configuration."""

    __tablename__ = "bot_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    platform: Mapped[str] = mapped_column(String(20))  # feishu | wecom | slack
    credentials_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="inactive")
    last_active_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    org_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class MemberPattern(Base):
    """Per-person pattern tracking."""

    __tablename__ = "member_patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    member_id: Mapped[str] = mapped_column(String(36), index=True)
    monster_id: Mapped[str] = mapped_column(String(100), index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    severity_avg: Mapped[float] = mapped_column(Float, default=1.0)
    last_seen: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
