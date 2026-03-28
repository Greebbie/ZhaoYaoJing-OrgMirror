"""WeCom (WeChat Work) bot handler.

Implements the BaseBotHandler interface for the WeCom platform. Acts as a thin
client that receives webhook events, parses commands, calls the core
ZhaoYaoJing API, and replies with Markdown messages.
"""

import logging
import time
from typing import Any

import httpx

from bots.base import BaseBotHandler
from bots.wecom.config import WeComConfig
from bots.wecom.templates import (
    build_mirror_report_md,
    build_self_check_md,
    build_xray_md,
)

logger = logging.getLogger(__name__)

# Cache for WeCom access token (simple in-memory, no external deps)
_TOKEN_CACHE: dict[str, Any] = {"token": "", "expires_at": 0}


class WeComBotHandler(BaseBotHandler):
    """WeCom webhook handler and message dispatcher."""

    platform: str = "wecom"

    def __init__(self, config: WeComConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(timeout=30.0)

    # ------------------------------------------------------------------
    # Webhook entry point
    # ------------------------------------------------------------------

    async def handle_webhook(self, request_body: dict) -> dict:
        """Main webhook entry point called by the FastAPI route.

        Handles two categories of incoming payloads:
        1. URL verification (used during WeCom app callback setup).
        2. Message callbacks (text messages, @mentions).

        Returns:
            Response dict to send back to WeCom.
        """
        # 1. URL verification (WeCom sends echostr for callback verification)
        if "echostr" in request_body:
            echostr = request_body.get("echostr", "")
            logger.info("WeCom URL verification received")
            return {"echostr": echostr}

        # 2. Message callback
        msg_type = request_body.get("MsgType", "")
        if msg_type == "text":
            await self._dispatch_text_message(request_body)
            return {"code": 0, "msg": "ok"}

        # 3. Event callback (e.g. subscribe, enter_agent)
        if msg_type == "event":
            event_type = request_body.get("Event", "")
            logger.info("WeCom event received: %s", event_type)
            return {"code": 0, "msg": "ok"}

        logger.debug("Unhandled WeCom message type: %s", msg_type)
        return {"code": 0, "msg": "ok"}

    # ------------------------------------------------------------------
    # Message dispatching
    # ------------------------------------------------------------------

    async def _dispatch_text_message(self, message: dict) -> None:
        """Route a text message to on_mention or on_message.

        WeCom application messages sent to the bot are treated as mentions.
        In group chats, messages containing @bot_name are mentions.
        """
        content = message.get("Content", "").strip()
        from_user = message.get("FromUserName", "")
        agent_id = message.get("AgentID", "")

        bot_name = self._config.bot_name
        is_mention = bot_name in content

        event = {
            "content": content.replace(f"@{bot_name}", "").strip(),
            "from_user": from_user,
            "agent_id": agent_id,
            "raw_message": message,
        }

        if is_mention:
            await self.on_mention(event)
        else:
            # Direct messages to the bot agent are treated as mentions
            await self.on_mention(event)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    async def on_mention(self, event: dict[str, Any]) -> None:
        """Handle @mention events.

        Extracts the message text, parses the command, and dispatches
        to the appropriate handler.
        """
        content = event.get("content", "")
        from_user = event.get("from_user", "")

        command, args = self.parse_command(content)

        logger.info(
            "WeCom mention from user=%s command=%s",
            from_user,
            command,
        )

        await self.on_command(command, args, event)

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
        from_user = event.get("from_user", "")
        raw_text = event.get("content", args)

        try:
            if command == "scan":
                content = args if args else raw_text
                report = await self._call_mirror_api(content)
                md = build_mirror_report_md(report, language="zh")
                await self.send_reply(from_user, md)

            elif command == "self-check":
                content = args if args else raw_text
                result = await self._call_self_mirror_api(content)
                md = build_self_check_md(result)
                await self.send_private(from_user, md)

            elif command == "xray":
                content = args if args else raw_text
                xray = await self._call_xray_api(content)
                md = build_xray_md(xray)
                await self.send_reply(from_user, md)

            elif command == "weekly":
                await self.send_reply(
                    from_user,
                    "\ud83d\udcc5 \u5468\u62a5\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85...",
                )

            elif command == "retro":
                await self.send_reply(
                    from_user,
                    "\ud83d\udd04 \u590d\u76d8\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85...",
                )

            else:
                # Default: treat the whole text as scan input
                report = await self._call_mirror_api(raw_text)
                md = build_mirror_report_md(report, language="zh")
                await self.send_reply(from_user, md)

        except httpx.HTTPStatusError as exc:
            logger.error(
                "API error: %s %s",
                exc.response.status_code,
                exc.response.text,
            )
            await self.send_reply(
                from_user,
                "\u26a0\ufe0f \u5206\u6790\u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
            )
        except httpx.RequestError as exc:
            logger.error("Network error calling internal API: %s", exc)
            await self.send_reply(
                from_user,
                "\u26a0\ufe0f \u7f51\u7edc\u8fde\u63a5\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
            )

    async def send_reply(
        self,
        channel_id: str,
        content: Any,
        reply_to: str | None = None,
    ) -> None:
        """Send a reply message via WeCom API.

        Uses the WeCom application message API to send Markdown content
        to a user or group chat.

        Args:
            channel_id: The user ID or chat ID to send to.
            content: Markdown string or plain text to send.
            reply_to: Unused for WeCom (no native thread reply support).
        """
        token = await self._get_access_token()
        url = f"{self._config.api_base_url}/message/send?access_token={token}"

        body: dict[str, Any] = {
            "touser": channel_id,
            "msgtype": "markdown",
            "agentid": self._config.agent_id,
            "markdown": {
                "content": content if isinstance(content, str) else str(content),
            },
        }

        resp = await self._http.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()

        errcode = data.get("errcode", 0)
        if errcode != 0:
            logger.error(
                "WeCom send_reply error: errcode=%s errmsg=%s",
                errcode,
                data.get("errmsg", ""),
            )
        else:
            logger.debug("WeCom message sent to %s", channel_id)

    async def send_private(self, user_id: str, content: Any) -> None:
        """Send a private/DM message to a user.

        WeCom application messages are inherently private when sent to a
        single user, so this delegates to send_reply with the user ID.

        Args:
            user_id: The WeCom user ID.
            content: Markdown string or plain text to send.
        """
        await self.send_reply(user_id, content)

    # ------------------------------------------------------------------
    # Command parsers (Chinese + English aliases)
    # ------------------------------------------------------------------

    def parse_command(self, text: str) -> tuple[str, str]:
        """Parse command from text, supporting both Chinese and English.

        Returns:
            (command, remaining_args) tuple.
        """
        command_map: dict[str, str] = {
            "\u626b\u63cf": "scan",
            "\u4e8b\u9879": "xray",
            "\u590d\u76d8": "retro",
            "\u5468\u62a5": "weekly",
            "\u81ea\u67e5": "self-check",
            "scan": "scan",
            "xray": "xray",
            "retro": "retro",
            "weekly": "weekly",
            "self-check": "self-check",
        }
        text = text.strip()
        for prefix, cmd in command_map.items():
            if text.startswith(prefix):
                return cmd, text[len(prefix) :].strip()
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
    # WeCom auth
    # ------------------------------------------------------------------

    async def _get_access_token(self) -> str:
        """Obtain (or refresh) a WeCom access token.

        Tokens are cached in-memory until they expire.

        Returns:
            Access token string.
        """
        now = time.time()
        if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now:
            return _TOKEN_CACHE["token"]

        url = (
            f"{self._config.api_base_url}/gettoken"
            f"?corpid={self._config.corp_id}"
            f"&corpsecret={self._config.secret}"
        )
        resp = await self._http.get(url)
        resp.raise_for_status()
        data = resp.json()

        errcode = data.get("errcode", 0)
        if errcode != 0:
            logger.error(
                "Failed to get WeCom access token: errcode=%s errmsg=%s",
                errcode,
                data.get("errmsg", ""),
            )
            raise RuntimeError(
                f"WeCom token error: {data.get('errmsg', 'unknown')}"
            )

        token = data.get("access_token", "")
        expires_in = data.get("expires_in", 7200)
        _TOKEN_CACHE["token"] = token
        _TOKEN_CACHE["expires_at"] = now + expires_in - 300  # refresh 5 min early

        logger.info(
            "WeCom access token refreshed (expires in %ds)", expires_in
        )
        return token
