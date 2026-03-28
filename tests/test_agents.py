import json
from unittest.mock import AsyncMock, patch

import pytest

from server.agents.base import AgentContext
from server.agents.intake import IntakeAgent
from server.agents.pipeline import AgentPipeline
from server.llm.base import LLMResponse


def _make_mock_router(response_content: str):
    mock = AsyncMock()
    mock.complete = AsyncMock(
        return_value=LLMResponse(content=response_content, model="mock", provider="mock")
    )
    return mock


@pytest.mark.asyncio
async def test_intake_agent():
    response = json.dumps({
        "statements": [
            {
                "speaker": "角色A",
                "content": "我觉得方向上是对的",
                "type": "claim",
                "references_people": [],
                "time_mentions": [],
                "items_mentioned": ["数据看板"],
            }
        ],
        "items": [{"name": "数据看板", "mentioned_by": ["角色A"], "status": "discussed"}],
        "people": [{"role_label": "角色A", "original_name": "张三"}],
    })
    router = _make_mock_router(response)
    agent = IntakeAgent(router)
    context = AgentContext({"content": "test", "anonymous_mode": True})
    result = await agent.run(context)

    assert len(result["intake_statements"]) == 1
    assert result["intake_statements"][0]["speaker"] == "角色A"
    assert len(result["intake_items"]) == 1


@pytest.mark.asyncio
async def test_pipeline_sequential():
    """Test that pipeline runs agents in sequence and accumulates context."""
    response1 = json.dumps({
        "statements": [{"speaker": "A", "content": "test", "type": "claim"}],
        "items": [],
        "people": [],
    })
    response2 = json.dumps({
        "checks": [],
        "completeness_score": 0.5,
        "critical_missing": ["owner"],
    })

    call_count = 0

    async def mock_complete(messages, **kwargs):
        nonlocal call_count
        call_count += 1
        content = response1 if call_count == 1 else response2
        return LLMResponse(content=content, model="mock", provider="mock")

    router = AsyncMock()
    router.complete = AsyncMock(side_effect=mock_complete)

    from server.agents.clarification import ClarificationAgent
    from server.agents.intake import IntakeAgent

    pipeline = AgentPipeline()
    pipeline.add_sequential(IntakeAgent(router))
    pipeline.add_sequential(ClarificationAgent(router))

    context = await pipeline.run({"content": "test", "anonymous_mode": True})
    assert "intake_statements" in context
    assert "completeness_score" in context


@pytest.mark.asyncio
async def test_mirror_endpoint_with_pipeline(client):
    """Test the refactored mirror endpoint using agent pipeline."""
    translations = [
        {
            "original": "test",
            "mirror": "translated",
            "monster_type": None,
            "confidence": 0.8,
        }
    ]
    monsters = []
    health = {"overall": 70, "dimensions": {
        "clarity": 70, "accountability": 70, "momentum": 70, "trust": 70
    }}
    recommendations = []

    call_count = 0

    async def mock_complete(messages, **kwargs):
        nonlocal call_count
        call_count += 1
        # Pipeline makes multiple LLM calls: intake, clarification, mirror(2), health, advisor
        if call_count <= 2:
            return LLMResponse(
                content=json.dumps({"statements": [], "items": [], "people": []}),
                model="mock", provider="mock",
            )
        elif call_count == 3:
            return LLMResponse(
                content=json.dumps({"translations": translations}),
                model="mock", provider="mock",
            )
        elif call_count == 4:
            return LLMResponse(
                content=json.dumps({"monsters": monsters}),
                model="mock", provider="mock",
            )
        elif call_count == 5:
            return LLMResponse(
                content=json.dumps(health),
                model="mock", provider="mock",
            )
        else:
            return LLMResponse(
                content=json.dumps({"recommendations": recommendations}),
                model="mock", provider="mock",
            )

    with patch("server.api.mirror.llm_router") as mock_router:
        mock_router.complete = AsyncMock(side_effect=mock_complete)
        response = await client.post(
            "/api/mirror",
            json={"content": "test content", "language": "zh"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert "monsters_detected" in data
    assert "health_score" in data


@pytest.mark.asyncio
async def test_self_mirror_endpoint(client):
    response_content = json.dumps({
        "patterns_detected": [
            {
                "monster_id": "phantom_ally",
                "text_segment": "我支持",
                "issue_zh": "社交性支持",
                "issue_en": "Phantom support",
            }
        ],
        "suggested_rewrite": "我支持，具体我可以...",
        "improvement_notes_zh": "增加具体承诺",
        "improvement_notes_en": "Add concrete commitment",
    })

    with patch("server.api.self_mirror.llm_router") as mock:
        mock.complete = AsyncMock(
            return_value=LLMResponse(content=response_content, model="m", provider="m")
        )
        response = await client.post(
            "/api/self-mirror",
            json={"content": "我觉得这个方向是对的，我支持"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["patterns_detected"]) == 1
    assert data["suggested_rewrite"] != ""


@pytest.mark.asyncio
async def test_xray_endpoint(client):
    response_content = json.dumps({
        "objective": "Build data dashboard",
        "deadline": "unspecified",
        "owner": "unassigned",
        "dependencies": ["API data"],
        "success_criteria": "undefined",
        "missing_info": ["owner", "deadline"],
        "blockers": ["resource constraints"],
    })

    with patch("server.api.xray.llm_router") as mock:
        mock.complete = AsyncMock(
            return_value=LLMResponse(content=response_content, model="m", provider="m")
        )
        response = await client.post(
            "/api/xray",
            json={"content": "数据看板需求，需要接入多个数据源"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["owner"] == "unassigned"
    assert "resource constraints" in data["blockers"]
