"""FastAPI router for the Feishu webhook endpoint.

Mount this router in the main FastAPI application to expose
POST /api/bot/feishu/webhook for receiving Feishu event callbacks.
"""

import logging

from fastapi import APIRouter, Request

from bots.feishu.bot import FeishuBotHandler
from bots.feishu.config import feishu_config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feishu-bot"])


@router.post("/api/bot/feishu/webhook")
async def feishu_webhook(request: Request) -> dict:
    """Receive and process Feishu event callbacks.

    This endpoint handles:
    - URL verification (during Feishu app setup)
    - im.message.receive_v1 events (user messages)
    - Card action callbacks (button interactions)

    Returns:
        JSON response expected by Feishu's event system.
    """
    body = await request.json()

    # Duplicate event protection: Feishu may retry events; log and acknowledge
    header = body.get("header", {})
    event_id = header.get("event_id", "")
    if event_id:
        logger.info("Feishu event received: id=%s type=%s", event_id, header.get("event_type"))

    handler = FeishuBotHandler(feishu_config)
    return await handler.handle_webhook(body)
