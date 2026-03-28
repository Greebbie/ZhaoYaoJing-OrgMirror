import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from server.llm.base import LLMResponse

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Canned responses for the 6 pipeline LLM calls
INTAKE_RESPONSE = json.dumps({
    "statements": [
        {"speaker": "角色A", "content": "方向上是对的", "type": "claim"},
    ],
    "items": [{"name": "数据看板", "mentioned_by": ["角色A"], "status": "discussed"}],
    "people": [{"role_label": "角色A", "original_name": "张三"}],
})

CLARIFICATION_RESPONSE = json.dumps({
    "checks": [
        {"item": "数据看板", "field": "owner", "status": "missing", "question": "谁负责？"}
    ],
    "completeness_score": 0.3,
    "critical_missing": ["owner", "deadline"],
})

TRANSLATION_RESPONSE = json.dumps({
    "translations": [
        {
            "original": "我觉得方向上是对的",
            "mirror": "口头支持，不代表我会做任何事",
            "monster_type": "phantom_ally",
            "confidence": 0.85,
        },
    ]
})

DETECTION_RESPONSE = json.dumps({
    "monsters": [
        {
            "monster_id": "phantom_ally",
            "monster_name_zh": "社交性支持妖",
            "monster_name_en": "The Phantom Ally",
            "emoji": "👻",
            "severity": 2,
            "evidence": ["我觉得方向上是对的"],
            "explanation_zh": "口头表态支持但无具体承诺",
            "explanation_en": "Verbal support with no concrete commitment",
            "confidence": 0.85,
        },
    ]
})

HEALTH_RESPONSE = json.dumps({
    "overall": 62,
    "dimensions": {"clarity": 45, "accountability": 35, "momentum": 50, "trust": 78},
})

ADVISOR_RESPONSE = json.dumps({
    "recommendations": [
        {
            "priority": "high",
            "action_zh": "直接问：你愿意做 owner 吗？",
            "action_en": "Ask directly: Are you willing to own this?",
            "rationale_zh": "需要明确责任人",
            "rationale_en": "Need clear ownership",
            "addressed_monsters": ["phantom_ally"],
        },
    ]
})

PIPELINE_RESPONSES = [
    INTAKE_RESPONSE,
    CLARIFICATION_RESPONSE,
    TRANSLATION_RESPONSE,
    DETECTION_RESPONSE,
    HEALTH_RESPONSE,
    ADVISOR_RESPONSE,
]


@pytest.fixture
def mock_llm():
    """Mock the LLM router for the full agent pipeline."""
    call_count = 0

    async def mock_complete(messages, **kwargs):
        nonlocal call_count
        idx = min(call_count, len(PIPELINE_RESPONSES) - 1)
        call_count += 1
        return LLMResponse(
            content=PIPELINE_RESPONSES[idx], model="mock", provider="mock"
        )

    with patch("server.api.mirror.llm_router") as mock_router:
        mock_router.complete = AsyncMock(side_effect=mock_complete)
        yield mock_router


@pytest.mark.asyncio
async def test_mirror_endpoint(client, mock_llm):
    demo_text = (FIXTURES_DIR / "chat_log_01.txt").read_text(encoding="utf-8")
    response = await client.post(
        "/api/mirror",
        json={
            "content": demo_text,
            "content_type": "chat_log",
            "language": "zh",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "translations" in data
    assert "monsters_detected" in data
    assert len(data["translations"]) > 0
    assert len(data["monsters_detected"]) > 0
    assert data["health_score"] is not None
    assert data["health_score"]["overall"] == 62
    assert len(data["recommendations"]) > 0

    # Check structure
    t = data["translations"][0]
    assert "original" in t
    assert "mirror" in t
    m = data["monsters_detected"][0]
    assert m["monster_id"] == "phantom_ally"


@pytest.mark.asyncio
async def test_mirror_empty_content(client):
    response = await client.post(
        "/api/mirror",
        json={"content": "  ", "content_type": "free_text"},
    )
    assert response.status_code == 400
