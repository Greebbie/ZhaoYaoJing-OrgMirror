"""Feishu (Lark) bot handler.

Implements the BaseBotHandler interface for the Feishu platform. Acts as a thin
client that receives webhook events, parses commands, calls the core
ZhaoYaoJing API, and replies with interactive message cards.
"""

import logging
import re
from typing import Any

import httpx

from bots.base import BaseBotHandler
from bots.feishu.cards import (
    build_mirror_report_card,
    build_self_check_card,
    build_xray_card,
)
from bots.feishu.config import FeishuConfig

logger = logging.getLogger(__name__)

# Cache for tenant access token (simple in-memory, no external deps)
_TOKEN_CACHE: dict[str, Any] = {"token": "", "expires_at": 0}


class FeishuBotHandler(BaseBotHandler):
    """Feishu webhook handler and message dispatcher."""

    platform: str = "feishu"

    def __init__(self, config: FeishuConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(timeout=30.0)

    # ------------------------------------------------------------------
    # Webhook entry point
    # ------------------------------------------------------------------

    async def handle_webhook(self, request_body: dict) -> dict:
        """Main webhook entry point called by the FastAPI route.

        Handles three categories of incoming payloads:
        1. URL verification challenge (used during Feishu app setup).
        2. Event callbacks (message received, mention, etc.).
        3. Card action callbacks (button clicks).

        Returns:
            Response dict to send back to Feishu.
        """
        # 1. URL verification
        if request_body.get("type") == "url_verification":
            challenge = request_body.get("challenge", "")
            logger.info("Feishu URL verification challenge received")
            return {"challenge": challenge}

        # 2. Event callback (v2 schema)
        header = request_body.get("header", {})
        event_type = header.get("event_type", "")
        event = request_body.get("event", {})

        if event_type == "im.message.receive_v1":
            await self._dispatch_message_event(event)
            return {"code": 0, "msg": "ok"}

        # 3. Card action callback
        if request_body.get("action"):
            logger.info("Card action received: %s", request_body.get("action"))
            return {"code": 0, "msg": "ok"}

        logger.debug("Unhandled event type: %s", event_type)
        return {"code": 0, "msg": "ok"}

    # ------------------------------------------------------------------
    # Event dispatching
    # ------------------------------------------------------------------

    async def _dispatch_message_event(self, event: dict) -> None:
        """Route a message event to on_mention or on_message."""
        message = event.get("message", {})
        mentions = message.get("mentions", [])

        # Check if the bot was @mentioned
        is_mentioned = any(
            m.get("name") == self._config.bot_name for m in mentions
        )

        if is_mentioned:
            await self.on_mention(event)
        else:
            await self.on_message(event)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    async def on_mention(self, event: dict[str, Any]) -> None:
        """Handle @mention events.

        Extracts the message text (with @bot prefix stripped), parses the
        command, and dispatches to the appropriate handler.
        """
        message = event.get("message", {})
        sender = event.get("sender", {}).get("sender_id", {})
        chat_id = message.get("chat_id", "")
        message_id = message.get("message_id", "")
        user_id = sender.get("open_id", "")

        text = self._extract_text(message)
        command, args = self.parse_command(text)

        logger.info(
            "Mention from user=%s chat=%s command=%s",
            user_id,
            chat_id,
            command,
        )

        await self.on_command(command, args, {
            "chat_id": chat_id,
            "message_id": message_id,
            "user_id": user_id,
            "raw_text": text,
            "message": message,
        })

    async def on_message(self, event: dict[str, Any]) -> None:
        """Handle messages in always-on mode (no mention required).

        Currently a placeholder -- in a future release this will auto-analyze
        messages when the bot is configured in always-on trigger mode.
        """
        logger.debug("on_message (always-on) -- not yet implemented")

    async def on_command(
        self, command: str, args: str, event: dict[str, Any]
    ) -> None:
        """Route a parsed command to the correct handler."""
        chat_id = event.get("chat_id", "")
        message_id = event.get("message_id")
        user_id = event.get("user_id", "")
        raw_text = event.get("raw_text", args)

        try:
            if command == "\u626b\u63cf" or command == "scan":
                content = args if args else raw_text
                report = await self._call_mirror_api(content)
                card = build_mirror_report_card(report, language="zh")
                await self.send_reply(chat_id, card, reply_to=message_id)

            elif command == "\u81ea\u67e5" or command == "self-check":
                content = args if args else raw_text
                result = await self._call_self_mirror_api(content)
                card = build_self_check_card(result)
                await self.send_private(user_id, card)

            elif command == "\u4e8b\u9879" or command == "xray":
                content = args if args else raw_text
                xray = await self._call_xray_api(content)
                card = build_xray_card(xray)
                await self.send_reply(chat_id, card, reply_to=message_id)

            elif command == "\u5468\u62a5" or command == "weekly":
                await self.send_reply(
                    chat_id,
                    self._text_card(
                        "\ud83d\udcc5 \u5468\u62a5\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85..."
                    ),
                    reply_to=message_id,
                )

            elif command == "\u590d\u76d8" or command == "retro":
                await self.send_reply(
                    chat_id,
                    self._text_card(
                        "\ud83d\udd04 \u590d\u76d8\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85..."
                    ),
                    reply_to=message_id,
                )

            else:
                # Default: treat the whole text as scan input
                report = await self._call_mirror_api(raw_text)
                card = build_mirror_report_card(report, language="zh")
                await self.send_reply(chat_id, card, reply_to=message_id)

        except httpx.HTTPStatusError as exc:
            logger.error("API error: %s %s", exc.response.status_code, exc.response.text)
            await self.send_reply(
                chat_id,
                self._text_card(
                    "\u26a0\ufe0f \u5206\u6790\u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"
                ),
                reply_to=message_id,
            )
        except httpx.RequestError as exc:
            logger.error("Network error calling internal API: %s", exc)
            await self.send_reply(
                chat_id,
                self._text_card(
                    "\u26a0\ufe0f \u7f51\u7edc\u8fde\u63a5\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"
                ),
                reply_to=message_id,
            )

    async def send_reply(
        self,
        channel_id: str,
        content: Any,
        reply_to: str | None = None,
    ) -> None:
        """Send a reply message to a Feishu chat.

        Args:
            channel_id: The chat_id (group or P2P) to send to.
            content: Card dict or plain text to send.
            reply_to: Optional message_id to reply to in thread.
        """
        token = await self._get_tenant_access_token()
        url = f"{self._config.api_base_url}/im/v1/messages"
        params: dict[str, str] = {"receive_id_type": "chat_id"}

        body: dict[str, Any] = {
            "receive_id": channel_id,
            "msg_type": content.get("msg_type", "interactive") if isinstance(content, dict) else "text",
            "content": self._serialize_content(content),
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        if reply_to:
            url = f"{self._config.api_base_url}/im/v1/messages/{reply_to}/reply"
            # Reply endpoint doesn't use receive_id
            body.pop("receive_id", None)
            params = {}

        resp = await self._http.post(url, json=body, headers=headers, params=params)
        resp.raise_for_status()
        logger.debug("Message sent: %s", resp.json().get("data", {}).get("message_id"))

    async def send_private(self, user_id: str, content: Any) -> None:
        """Send a private/DM message to a user.

        Args:
            user_id: The open_id of the target user.
            content: Card dict or plain text to send.
        """
        token = await self._get_tenant_access_token()
        url = f"{self._config.api_base_url}/im/v1/messages"
        params = {"receive_id_type": "open_id"}

        body: dict[str, Any] = {
            "receive_id": user_id,
            "msg_type": content.get("msg_type", "interactive") if isinstance(content, dict) else "text",
            "content": self._serialize_content(content),
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        resp = await self._http.post(url, json=body, headers=headers, params=params)
        resp.raise_for_status()
        logger.debug("Private message sent to %s", user_id)

    # ------------------------------------------------------------------
    # Command parsers (Chinese + English aliases)
    # ------------------------------------------------------------------

    def parse_command(self, text: str) -> tuple[str, str]:
        """Parse command from text, supporting both Chinese and English.

        Returns:
            (command, remaining_args) tuple.
        """
        command_map: dict[str, str] = {
            "\u626b\u63cf": "scan",     # scan
            "\u4e8b\u9879": "xray",     # xray
            "\u590d\u76d8": "retro",    # retro
            "\u5468\u62a5": "weekly",   # weekly
            "\u81ea\u67e5": "self-check",  # self-check
            "scan": "scan",
            "xray": "xray",
            "retro": "retro",
            "weekly": "weekly",
            "self-check": "self-check",
        }
        text = text.strip()
        for prefix, cmd in command_map.items():
            if text.startswith(prefix):
                return cmd, text[len(prefix):].strip()
        return "scan", text  # Default to scan

    # ------------------------------------------------------------------
    # Internal API calls
    # ------------------------------------------------------------------

    async def _call_mirror_api(
        self,
        content: str,
        trigger_mode: str = "bot_mention",
    ) -> dict:
        """Call POST /api/mirror on the core service.

        Args:
            content: The text to analyze.
            trigger_mode: How the analysis was triggered.

        Returns:
            Parsed JSON response (MirrorReport shape).
        """
        url = f"{self._config.mirror_api_base_url}/api/mirror"
        payload = {
            "content": content,
            "content_type": "free_text",
            "language": "zh",
            "trigger_mode": trigger_mode,
            "anonymous_mode": True,
        }
        resp = await self._http.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _call_self_mirror_api(self, content: str) -> dict:
        """Call POST /api/self-mirror on the core service.

        Returns:
            Parsed JSON response (SelfMirrorResult shape).
        """
        url = f"{self._config.mirror_api_base_url}/api/self-mirror"
        payload = {"content": content, "language": "zh"}
        resp = await self._http.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _call_xray_api(self, content: str) -> dict:
        """Call POST /api/xray on the core service.

        Returns:
            Parsed JSON response (XRay shape).
        """
        url = f"{self._config.mirror_api_base_url}/api/xray"
        payload = {"content": content, "content_type": "requirement_doc"}
        resp = await self._http.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Feishu auth
    # ------------------------------------------------------------------

    async def _get_tenant_access_token(self) -> str:
        """Obtain (or refresh) a Feishu tenant access token.

        Tokens are cached in-memory until they expire.

        Returns:
            Bearer token string.
        """
        import time

        now = time.time()
        if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now:
            return _TOKEN_CACHE["token"]

        url = f"{self._config.api_base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self._config.app_id,
            "app_secret": self._config.app_secret,
        }
        resp = await self._http.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        token = data.get("tenant_access_token", "")
        expire = data.get("expire", 7200)  # default 2 hours
        _TOKEN_CACHE["token"] = token
        _TOKEN_CACHE["expires_at"] = now + expire - 300  # refresh 5 min early

        logger.info("Feishu tenant access token refreshed (expires in %ds)", expire)
        return token

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_text(self, message: dict) -> str:
        """Extract plain text from a Feishu message payload.

        Handles both rich-text and plain text content formats,
        stripping @mention tags.
        """
        import json as json_mod

        content_str = message.get("content", "{}")
        try:
            content_obj = json_mod.loads(content_str)
        except (json_mod.JSONDecodeError, TypeError):
            content_obj = {}

        # Plain text message
        text = content_obj.get("text", "")

        # Strip @mention tags like @_user_1
        text = re.sub(r"@_user_\d+\s*", "", text).strip()

        return text

    @staticmethod
    def _text_card(text: str) -> dict:
        """Build a minimal text-only card."""
        return {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": text},
                    }
                ],
            },
        }

    @staticmethod
    def _serialize_content(content: Any) -> str:
        """Serialize card or text content to the string format Feishu expects."""
        import json as json_mod

        if isinstance(content, dict):
            # Feishu expects the card object serialized as a JSON string
            card = content.get("card", content)
            return json_mod.dumps(card, ensure_ascii=False)
        return json_mod.dumps({"text": str(content)}, ensure_ascii=False)
