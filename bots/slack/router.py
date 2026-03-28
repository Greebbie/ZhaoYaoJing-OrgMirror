"""FastAPI router for the Slack bot endpoints.

Mount this router in the main FastAPI application to expose:
- POST /api/bot/slack/events   - Slack Events API endpoint
- POST /api/bot/slack/commands - Slack slash commands endpoint
"""

import logging

from fastapi import APIRouter, Request

from bots.slack.bot import SlackBotHandler
from bots.slack.config import slack_config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["slack-bot"])


@router.post("/api/bot/slack/events")
async def slack_events(request: Request) -> dict:
    """Receive and process Slack Events API callbacks.

    This endpoint handles:
    - URL verification (during Slack app Event Subscriptions setup)
    - app_mention events (user @mentions the bot)
    - message events (DMs and channel messages)

    Returns:
        JSON response expected by Slack's Events API.
    """
    body = await request.json()

    event_id = body.get("event_id", "")
    if event_id:
        event = body.get("event", {})
        logger.info(
            "Slack event received: id=%s type=%s",
            event_id,
            event.get("type"),
        )

    handler = SlackBotHandler(slack_config)
    return await handler.handle_event(body)


@router.post("/api/bot/slack/commands")
async def slack_commands(request: Request) -> dict:
    """Receive and process Slack slash commands.

    This endpoint handles slash commands like:
    - /mirror [text]  - Run mirror analysis
    - /xray [text]    - Run X-ray analysis
    - /report         - Generate self-check report (sent as DM)

    The actual response is sent asynchronously via chat.postMessage;
    this endpoint returns an immediate acknowledgement.

    Returns:
        JSON response for immediate Slack acknowledgement.
    """
    form_data = await request.form()
    parsed: dict[str, str] = {k: str(v) for k, v in form_data.items()}

    logger.info(
        "Slack slash command received: %s from user=%s",
        parsed.get("command"),
        parsed.get("user_id"),
    )

    handler = SlackBotHandler(slack_config)
    return await handler.handle_slash_command(parsed)
