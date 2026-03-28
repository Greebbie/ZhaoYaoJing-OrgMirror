import pytest

from server.db.models import MirrorResult
from server.db.repositories import ReportRepository
from tests.conftest import test_session_factory


async def _seed_reports(count: int = 3):
    async with test_session_factory() as session:
        repo = ReportRepository(session)
        for i in range(count):
            await repo.create(
                MirrorResult(
                    input_text=f"test input {i}",
                    content_type="chat_log",
                    trigger_mode="manual",
                    language="zh",
                    translations_json=[{"original": f"t{i}", "mirror": f"m{i}"}],
                    monsters_json=[
                        {"monster_id": "phantom_ally", "severity": 2}
                    ],
                    health_score_json={"overall": 60 + i},
                    recommendations_json=[],
                )
            )


@pytest.mark.asyncio
async def test_list_reports_endpoint(client):
    await _seed_reports(3)
    response = await client.get("/api/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["reports"]) == 3


@pytest.mark.asyncio
async def test_get_report_not_found(client):
    response = await client.get("/api/reports/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_save_and_get_org_config(client):
    response = await client.post(
        "/api/org/config",
        json={"name": "My Org", "org_type": "corp", "size": "30-100"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "saved"

    response = await client.get("/api/org/config")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Org"
    assert data["org_type"] == "corp"


@pytest.mark.asyncio
async def test_weekly_report(client):
    await _seed_reports(2)
    response = await client.post("/api/report/weekly")
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyses"] == 2
