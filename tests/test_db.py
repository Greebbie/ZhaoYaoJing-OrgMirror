import pytest

from server.db.models import Item, MirrorResult, OrgConfig
from server.db.repositories import (
    ItemRepository,
    OrgConfigRepository,
    PatternRepository,
    ReportRepository,
)


@pytest.mark.asyncio
async def test_create_and_get_report(db_session):
    repo = ReportRepository(db_session)
    result = MirrorResult(
        input_text="test input",
        content_type="chat_log",
        trigger_mode="manual",
        language="zh",
        translations_json=[{"original": "test", "mirror": "translated"}],
        monsters_json=[{"monster_id": "phantom_ally", "severity": 2}],
        health_score_json={"overall": 65},
        recommendations_json=[],
    )
    saved = await repo.create(result)
    assert saved.id is not None

    fetched = await repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.input_text == "test input"
    assert len(fetched.translations_json) == 1


@pytest.mark.asyncio
async def test_list_reports(db_session):
    repo = ReportRepository(db_session)
    for i in range(3):
        await repo.create(
            MirrorResult(
                input_text=f"test {i}",
                content_type="chat_log",
                trigger_mode="manual",
            )
        )
    results = await repo.list_recent(limit=10)
    assert len(results) == 3
    count = await repo.count()
    assert count == 3


@pytest.mark.asyncio
async def test_pattern_upsert(db_session):
    repo = PatternRepository(db_session)
    await repo.upsert("phantom_ally", severity=2.0)
    await repo.upsert("phantom_ally", severity=3.0)
    await repo.upsert("meeting_vortex", severity=1.0)

    top = await repo.get_top_monsters(limit=5)
    assert len(top) == 2
    # phantom_ally should be first (2 occurrences)
    assert top[0].monster_id == "phantom_ally"
    assert top[0].occurrence_count == 2
    assert top[0].severity_avg == 2.5  # (2+3)/2


@pytest.mark.asyncio
async def test_org_config(db_session):
    repo = OrgConfigRepository(db_session)
    config = OrgConfig(
        name="Test Org",
        org_type="startup",
        size="10-30",
        config_json={"pain_points": ["things_stuck"]},
    )
    saved = await repo.save(config)
    assert saved.id is not None

    latest = await repo.get_latest()
    assert latest is not None
    assert latest.name == "Test Org"


@pytest.mark.asyncio
async def test_item_repository(db_session):
    repo = ItemRepository(db_session)
    item = Item(name="Data Dashboard", description="Build data dashboard")
    saved = await repo.create(item)
    assert saved.id is not None

    fetched = await repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.name == "Data Dashboard"

    all_items = await repo.list_all()
    assert len(all_items) == 1
