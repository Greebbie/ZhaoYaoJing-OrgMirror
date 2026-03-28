import datetime
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.db.database import get_session
from server.db.models import BotConnection

logger = logging.getLogger(__name__)
router = APIRouter()

# Platform-specific test URLs
PLATFORM_TEST_URLS = {
    "feishu": "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    "wecom": "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
    "slack": "https://slack.com/api/auth.test",
}


class BotConnectionInput(BaseModel):
    platform: str  # feishu | wecom | slack
    credentials: dict


class BotConnectionResponse(BaseModel):
    id: str
    platform: str
    status: str
    webhook_url: str
    last_active_at: str | None
    created_at: str
    credentials_keys: list[str]  # Only show which keys are set, not values


def _webhook_url(platform: str) -> str:
    urls = {
        "feishu": "/api/bot/feishu/webhook",
        "wecom": "/api/bot/wecom/webhook",
        "slack": "/api/bot/slack/events",
    }
    return urls.get(platform, "")


def _to_response(bot: BotConnection) -> BotConnectionResponse:
    creds = bot.credentials_json or {}
    return BotConnectionResponse(
        id=bot.id,
        platform=bot.platform,
        status=bot.status,
        webhook_url=_webhook_url(bot.platform),
        last_active_at=bot.last_active_at.isoformat() if bot.last_active_at else None,
        created_at=bot.created_at.isoformat() if bot.created_at else "",
        credentials_keys=[k for k, v in creds.items() if v],
    )


@router.get("/api/admin/bots")
async def list_bots(session: AsyncSession = Depends(get_session)):
    stmt = select(BotConnection).order_by(desc(BotConnection.created_at))
    result = await session.execute(stmt)
    bots = result.scalars().all()
    return {"bots": [_to_response(b) for b in bots]}


@router.post("/api/admin/bots")
async def create_bot(
    data: BotConnectionInput,
    session: AsyncSession = Depends(get_session),
):
    if data.platform not in ("feishu", "wecom", "slack"):
        raise HTTPException(status_code=400, detail="Invalid platform")

    # Check for existing connection on same platform
    existing = await session.execute(
        select(BotConnection).where(BotConnection.platform == data.platform)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Bot connection for {data.platform} already exists. Delete it first.",
        )

    bot = BotConnection(
        platform=data.platform,
        credentials_json=data.credentials,
        status="inactive",
    )
    session.add(bot)
    await session.commit()
    await session.refresh(bot)

    return _to_response(bot)


@router.delete("/api/admin/bots/{bot_id}")
async def delete_bot(
    bot_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(BotConnection).where(BotConnection.id == bot_id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot connection not found")

    await session.execute(
        delete(BotConnection).where(BotConnection.id == bot_id)
    )
    await session.commit()
    return {"status": "deleted"}


@router.post("/api/admin/bots/{bot_id}/test")
async def test_bot(
    bot_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Test bot connection by calling platform API."""
    result = await session.execute(
        select(BotConnection).where(BotConnection.id == bot_id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot connection not found")

    creds = bot.credentials_json or {}
    platform = bot.platform

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if platform == "feishu":
                resp = await client.post(
                    PLATFORM_TEST_URLS["feishu"],
                    json={
                        "app_id": creds.get("app_id", ""),
                        "app_secret": creds.get("app_secret", ""),
                    },
                )
                data = resp.json()
                ok = data.get("code") == 0
                msg = data.get("msg", "Unknown error")

            elif platform == "wecom":
                resp = await client.get(
                    PLATFORM_TEST_URLS["wecom"],
                    params={
                        "corpid": creds.get("corp_id", ""),
                        "corpsecret": creds.get("secret", ""),
                    },
                )
                data = resp.json()
                ok = data.get("errcode") == 0
                msg = data.get("errmsg", "Unknown error")

            elif platform == "slack":
                resp = await client.post(
                    PLATFORM_TEST_URLS["slack"],
                    headers={
                        "Authorization": f"Bearer {creds.get('bot_token', '')}",
                    },
                )
                data = resp.json()
                ok = data.get("ok", False)
                msg = data.get("error", "Success" if ok else "Unknown error")
            else:
                ok = False
                msg = "Unknown platform"

        # Update status
        bot.status = "active" if ok else "error"
        bot.last_active_at = datetime.datetime.now(datetime.UTC) if ok else None
        await session.commit()

        return {
            "status": "connected" if ok else "error",
            "message": msg,
            "webhook_url": _webhook_url(platform),
        }

    except httpx.RequestError as e:
        bot.status = "error"
        await session.commit()
        return {"status": "error", "message": f"Connection failed: {e}"}
