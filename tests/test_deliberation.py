import json
from unittest.mock import AsyncMock, patch

import pytest

from server.llm.base import LLMResponse

ADVOCATE_RESPONSE = json.dumps({
    "party": "产品经理",
    "position": "support",
    "position_statement": "我支持推进数据看板",
    "core_constraints": ["人力有限", "Q2有其他优先项"],
    "minimum_acceptable_outcome": "至少出一个MVP",
    "alternative_proposal": "先做轻量版",
    "key_concerns": ["开发资源可能不够"],
})

CROSS_EXAM_RESPONSE = json.dumps({
    "party": "产品经理",
    "contradictions_found": [
        {
            "target_party": "开发负责人",
            "issue": "声称资源紧张但没给具体排期",
            "evidence": "多次提到资源紧但无替代方案",
        }
    ],
    "questions": [
        {"target_party": "开发负责人", "question": "最早什么时候能开始？"}
    ],
    "position_revised": False,
    "revised_position": None,
})

ARBITER_RESPONSE = json.dumps({
    "conflict_type": "resource_conflict",
    "parties_summary": [
        {"role": "产品经理", "position": "support", "constraints": ["人力有限"]},
        {"role": "开发负责人", "position": "conditional", "constraints": ["资源紧张"]},
    ],
    "options": [
        {
            "label": "方案A: MVP优先",
            "description": "先做轻量版MVP，2周内交付",
            "trade_offs": ["功能有限", "但能快速验证"],
        },
        {
            "label": "方案B: 完整版排期",
            "description": "等Q3资源释放后做完整版",
            "trade_offs": ["功能完整", "但需等待2个月"],
        },
    ],
    "unresolved": ["具体开发人员分配"],
    "recommended_option": "方案A: MVP优先",
    "escalation_recommendation": None,
})


@pytest.fixture
def mock_deliberation_llm():
    """Mock LLM for deliberation flow."""
    call_count = 0

    async def mock_complete(messages, **kwargs):
        nonlocal call_count
        call_count += 1
        # Round 1: 2 advocate calls, Round 2: 2 cross-exam calls, Round 3: 1 arbiter
        if call_count <= 2:
            content = ADVOCATE_RESPONSE
        elif call_count <= 4:
            content = CROSS_EXAM_RESPONSE
        else:
            content = ARBITER_RESPONSE
        return LLMResponse(content=content, model="mock", provider="mock")

    with patch("server.api.deliberate.llm_router") as mock:
        mock.complete = AsyncMock(side_effect=mock_complete)
        yield mock


@pytest.mark.asyncio
async def test_deliberation_endpoint(client, mock_deliberation_llm):
    response = await client.post(
        "/api/deliberate",
        json={
            "content": "数据看板需求讨论，产品想做，开发说资源紧",
            "parties": ["产品经理（推动需求方）", "开发负责人（资源受限方）"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rounds_completed"] == 3
    assert data["parties_count"] == 2
    assert len(data["advocate_positions"]) == 2
    assert "deliberation" in data
    assert "options" in data["deliberation"]


@pytest.mark.asyncio
async def test_deliberation_too_few_parties(client):
    response = await client.post(
        "/api/deliberate",
        json={"content": "some text", "parties": ["only one"]},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_deliberation_too_many_parties(client):
    response = await client.post(
        "/api/deliberate",
        json={
            "content": "some text",
            "parties": [f"party{i}" for i in range(6)],
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_deliberation_empty_content(client):
    response = await client.post(
        "/api/deliberate",
        json={"content": "  ", "parties": ["a", "b"]},
    )
    assert response.status_code == 400
