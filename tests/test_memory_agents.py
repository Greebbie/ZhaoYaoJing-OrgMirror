import json
from unittest.mock import AsyncMock

import pytest

from server.agents.base import AgentContext
from server.agents.drift import DriftAgent
from server.agents.escalation import EscalationAgent
from server.agents.memory import MemoryAgent
from server.llm.base import LLMResponse


def _mock_router(response_content: str):
    mock = AsyncMock()
    mock.complete = AsyncMock(
        return_value=LLMResponse(
            content=response_content, model="mock", provider="mock"
        )
    )
    return mock


@pytest.mark.asyncio
async def test_memory_agent():
    response = json.dumps({
        "recurring_patterns": [
            {
                "monster_id": "phantom_ally",
                "total_occurrences": 5,
                "trend": "increasing",
                "note_zh": "社交性支持妖在过去30天出现5次",
                "note_en": "Phantom Ally detected 5 times in past 30 days",
            }
        ],
        "history_summary_zh": "团队社交性支持问题持续恶化",
        "history_summary_en": "Team phantom support issue worsening",
    })
    router = _mock_router(response)
    agent = MemoryAgent(router)

    context = AgentContext({
        "monsters_detected": [
            {"monster_id": "phantom_ally", "severity": 2}
        ],
        "pattern_history": [
            {"monster_id": "phantom_ally", "count": 4, "last_seen": "2026-03-20"}
        ],
    })
    result = await agent.run(context)

    assert len(result["memory_patterns"]) == 1
    assert result["memory_patterns"][0]["monster_id"] == "phantom_ally"
    assert result["memory_patterns"][0]["total_occurrences"] == 5
    assert result["history_summary_zh"] != ""


@pytest.mark.asyncio
async def test_memory_agent_no_monsters():
    router = _mock_router("{}")
    agent = MemoryAgent(router)
    context = AgentContext({"monsters_detected": []})
    result = await agent.run(context)
    assert result["memory_patterns"] == []


@pytest.mark.asyncio
async def test_drift_agent():
    response = json.dumps({
        "drifts_detected": [
            {
                "field": "deadline",
                "previous": "2026-04-01",
                "current": "2026-04-15",
                "drift_type": "shifted",
                "severity": 2,
                "note_zh": "截止日期后移了2周",
                "note_en": "Deadline shifted back by 2 weeks",
            }
        ],
        "drift_score": 0.6,
        "summary_zh": "检测到1处漂移",
        "summary_en": "1 drift detected",
    })
    router = _mock_router(response)
    agent = DriftAgent(router)

    context = AgentContext({
        "xray": {"deadline": "2026-04-15", "owner": "Role A"},
        "previous_xray": {"deadline": "2026-04-01", "owner": "Role A"},
    })
    result = await agent.run(context)

    assert len(result["drifts_detected"]) == 1
    assert result["drifts_detected"][0]["field"] == "deadline"
    assert result["drift_score"] == 0.6


@pytest.mark.asyncio
async def test_drift_agent_no_baseline():
    router = _mock_router("{}")
    agent = DriftAgent(router)
    context = AgentContext({"xray": {"deadline": "2026-04-01"}})
    result = await agent.run(context)
    assert result["drifts_detected"] == []
    assert result["drift_score"] == 0.0


@pytest.mark.asyncio
async def test_escalation_agent():
    response = json.dumps({
        "escalation_items": [
            {
                "item_name": "数据看板",
                "days_stale": 14,
                "owner": "Role A",
                "summary_zh": "数据看板需求已停滞14天",
                "summary_en": "Data dashboard requirement stale for 14 days",
                "monsters_involved": ["phantom_ally", "ghost_owner"],
                "suggested_action_zh": "重新指定Owner或正式搁置",
                "suggested_action_en": "Reassign owner or formally shelve",
                "urgency": "high",
            }
        ]
    })
    router = _mock_router(response)
    agent = EscalationAgent(router)

    context = AgentContext({
        "stale_items": [
            {"name": "数据看板", "owner": "Role A", "days_stale": 14}
        ],
        "monsters_detected": [{"monster_id": "ghost_owner"}],
    })
    result = await agent.run(context)

    assert len(result["escalation_items"]) == 1
    assert result["escalation_items"][0]["urgency"] == "high"


@pytest.mark.asyncio
async def test_escalation_agent_no_stale():
    router = _mock_router("{}")
    agent = EscalationAgent(router)
    context = AgentContext({})
    result = await agent.run(context)
    assert result["escalation_items"] == []
