"""FastAPI router for the WeCom webhook endpoint.

Mount this router in the main FastAPI application to expose
POST /api/bot/wecom/webhook for receiving WeCom event callbacks.
"""

import logging

from fastapi import APIRouter, Request

from bots.wecom.bot import WeComBotHandler
from bots.wecom.config import wecom_config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["wecom-bot"])


@router.post("/api/bot/wecom/webhook")
async def wecom_webhook(request: Request) -> dict:
    """Receive and process WeCom event callbacks.

    This endpoint handles:
    - URL verification (during WeCom app callback setup)
    - Text message callbacks (user messages)
    - Event callbacks (subscribe, enter_agent, etc.)

    Returns:
        JSON response expected by WeCom's event system.
    """
    body = await request.json()

    msg_id = body.get("MsgId", "")
    if msg_id:
        logger.info(
            "WeCom message received: id=%s type=%s",
            msg_id,
            body.get("MsgType"),
        )

    handler = WeComBotHandler(wecom_config)
    return await handler.handle_webhook(body)
