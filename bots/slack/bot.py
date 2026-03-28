"""Slack bot handler.

Implements the BaseBotHandler interface for the Slack platform. Acts as a thin
client that receives event callbacks and slash commands, calls the core
ZhaoYaoJing API, and replies with Block Kit messages.
"""

import hashlib
import hmac
import logging
import re
import time
from typing import Any

import httpx

from bots.base import BaseBotHandler
from bots.slack.blocks import (
    build_mirror_report_blocks,
    build_self_check_blocks,
    build_xray_blocks,
)
from bots.slack.config import SlackConfig

logger = logging.getLogger(__name__)


class SlackBotHandler(BaseBotHandler):
    """Slack event and slash command handler."""

    platform: str = "slack"

    def __init__(self, config: SlackConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(timeout=30.0)

    # ------------------------------------------------------------------
    # Event entry point
    # ------------------------------------------------------------------

    async def handle_event(self, event_data: dict) -> dict:
        """Main event entry point called by the FastAPI route.

        Handles three categories of incoming payloads:
        1. URL verification challenge (used during Slack app setup).
        2. Event callbacks (message, app_mention).
        3. Slash command payloads (routed separately).

        Returns:
            Response dict to send back to Slack.
        """
        # 1. URL verification
        if event_data.get("type") == "url_verification":
            challenge = event_data.get("challenge", "")
            logger.info("Slack URL verification challenge received")
            return {"challenge": challenge}

        # 2. Event callback
        if event_data.get("type") == "event_callback":
            event = event_data.get("event", {})
            event_type = event.get("type", "")

            # Ignore bot's own messages to prevent loops
            if event.get("bot_id"):
                return {"ok": True}

            if event_type == "app_mention":
                await self.on_mention(event)
                return {"ok": True}

            if event_type == "message":
                # DMs to the bot (channel type "im")
                channel_type = event.get("channel_type", "")
                if channel_type == "im":
                    await self.on_mention(event)
                else:
                    await self.on_message(event)
                return {"ok": True}

            logger.debug("Unhandled Slack event type: %s", event_type)
            return {"ok": True}

        logger.debug("Unhandled Slack payload type: %s", event_data.get("type"))
        return {"ok": True}

    # ------------------------------------------------------------------
    # Slash command entry point
    # ------------------------------------------------------------------

    async def handle_slash_command(self, form_data: dict) -> dict:
        """Handle Slack slash commands (/mirror, /xray, /report).

        Args:
            form_data: Parsed form data from the slash command request.

        Returns:
            Immediate response dict (Slack expects a response within 3s).
        """
        command_name = form_data.get("command", "").lstrip("/")
        text = form_data.get("text", "").strip()
        user_id = form_data.get("user_id", "")
        channel_id = form_data.get("channel_id", "")

        logger.info(
            "Slack slash command: /%s from user=%s channel=%s",
            command_name,
            user_id,
            channel_id,
        )

        # Map slash commands to internal commands
        command_map: dict[str, str] = {
            "mirror": "scan",
            "xray": "xray",
            "report": "self-check",
        }

        internal_cmd = command_map.get(command_name, "scan")
        event = {
            "channel": channel_id,
            "user": user_id,
            "text": text,
            "ts": form_data.get("trigger_id", ""),
        }

        await self.on_command(internal_cmd, text, event)

        # Return empty 200 -- the actual response is sent via chat.postMessage
        return {"response_type": "in_channel"}

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    async def on_mention(self, event: dict[str, Any]) -> None:
        """Handle @mention and DM events.

        Extracts the message text (with @bot mention stripped), parses the
        command, and dispatches to the appropriate handler. Supports
        thread-aware analysis by grabbing thread messages.
        """
        text = event.get("text", "")
        channel = event.get("channel", "")
        user = event.get("user", "")
        ts = event.get("ts", "")
        thread_ts = event.get("thread_ts")

        # Strip @bot mention from text
        text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

        # If message is in a thread, gather thread context
        if thread_ts and thread_ts != ts:
            thread_text = await self._get_thread_text(channel, thread_ts)
            if thread_text:
                text = f"{thread_text}\n\n---\n{text}"

        command, args = self.parse_command(text)

        logger.info(
            "Slack mention from user=%s channel=%s command=%s",
            user,
            channel,
            command,
        )

        await self.on_command(command, args, {
            "channel": channel,
            "user": user,
            "ts": ts,
            "thread_ts": thread_ts or ts,
            "raw_text": text,
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
        channel = event.get("channel", "")
        user = event.get("user", "")
        thread_ts = event.get("thread_ts")
        raw_text = event.get("raw_text", args)

        try:
            if command == "scan":
                content = args if args else raw_text
                report = await self._call_mirror_api(content)
                blocks = build_mirror_report_blocks(report, language="zh")
                await self.send_reply(channel, blocks, reply_to=thread_ts)

            elif command == "self-check":
                content = args if args else raw_text
                result = await self._call_self_mirror_api(content)
                blocks = build_self_check_blocks(result)
                await self.send_private(user, blocks)

            elif command == "xray":
                content = args if args else raw_text
                xray = await self._call_xray_api(content)
                blocks = build_xray_blocks(xray)
                await self.send_reply(channel, blocks, reply_to=thread_ts)

            elif command == "weekly":
                await self.send_reply(
                    channel,
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "\ud83d\udcc5 \u5468\u62a5\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85...",
                            },
                        }
                    ],
                    reply_to=thread_ts,
                )

            elif command == "retro":
                await self.send_reply(
                    channel,
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "\ud83d\udd04 \u590d\u76d8\u529f\u80fd\u5f00\u53d1\u4e2d\uff0c\u656c\u8bf7\u671f\u5f85...",
                            },
                        }
                    ],
                    reply_to=thread_ts,
                )

            else:
                # Default: treat the whole text as scan input
                report = await self._call_mirror_api(raw_text)
                blocks = build_mirror_report_blocks(report, language="zh")
                await self.send_reply(channel, blocks, reply_to=thread_ts)

        except httpx.HTTPStatusError as exc:
            logger.error(
                "API error: %s %s",
                exc.response.status_code,
                exc.response.text,
            )
            await self.send_reply(
                channel,
                [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\u26a0\ufe0f \u5206\u6790\u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
                        },
                    }
                ],
                reply_to=thread_ts,
            )
        except httpx.RequestError as exc:
            logger.error("Network error calling internal API: %s", exc)
            await self.send_reply(
                channel,
                [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\u26a0\ufe0f \u7f51\u7edc\u8fde\u63a5\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
                        },
                    }
                ],
                reply_to=thread_ts,
            )

    async def send_reply(
        self,
        channel_id: str,
        content: Any,
        reply_to: str | None = None,
    ) -> None:
        """Send a reply message to a Slack channel using Block Kit blocks.

        Args:
            channel_id: The channel ID to post to.
            content: List of Block Kit block dicts or a plain text string.
            reply_to: Optional thread_ts to reply in a thread.
        """
        url = f"{self._config.api_base_url}/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self._config.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        body: dict[str, Any] = {"channel": channel_id}

        if isinstance(content, list):
            body["blocks"] = content
            # Provide fallback text for notifications
            body["text"] = "\ud83e\ude9e \u7167\u5996\u955c\u5206\u6790\u7ed3\u679c"
        else:
            body["text"] = str(content)

        if reply_to:
            body["thread_ts"] = reply_to

        resp = await self._http.post(url, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("ok"):
            logger.error(
                "Slack send_reply error: %s", data.get("error", "unknown")
            )
        else:
            logger.debug(
                "Slack message sent: channel=%s ts=%s",
                channel_id,
                data.get("ts"),
            )

    async def send_private(self, user_id: str, content: Any) -> None:
        """Send a private/DM message to a user.

        Opens a DM conversation via conversations.open and then posts
        the message to that DM channel.

        Args:
            user_id: The Slack user ID.
            content: List of Block Kit block dicts or a plain text string.
        """
        # Open DM channel
        open_url = f"{self._config.api_base_url}/conversations.open"
        headers = {
            "Authorization": f"Bearer {self._config.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        open_resp = await self._http.post(
            open_url,
            json={"users": user_id},
            headers=headers,
        )
        open_resp.raise_for_status()
        open_data = open_resp.json()

        if not open_data.get("ok"):
            logger.error(
                "Slack conversations.open error: %s",
                open_data.get("error", "unknown"),
            )
            return

        dm_channel = open_data["channel"]["id"]

        # Send message to DM channel
        await self.send_reply(dm_channel, content)

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
    # Slack helpers
    # ------------------------------------------------------------------

    async def _get_thread_text(self, channel: str, thread_ts: str) -> str:
        """Fetch all messages in a thread and concatenate their text.

        This enables thread-aware analysis: when a user mentions the bot
        in a thread, we gather the full thread context.

        Args:
            channel: Channel ID containing the thread.
            thread_ts: Timestamp of the parent message.

        Returns:
            Concatenated thread text, or empty string on failure.
        """
        url = f"{self._config.api_base_url}/conversations.replies"
        headers = {
            "Authorization": f"Bearer {self._config.bot_token}",
        }
        params = {"channel": channel, "ts": thread_ts, "limit": "50"}

        try:
            resp = await self._http.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("ok"):
                logger.warning(
                    "Failed to fetch thread: %s", data.get("error")
                )
                return ""

            messages = data.get("messages", [])
            # Skip bot messages to avoid recursion
            texts = [
                m.get("text", "")
                for m in messages
                if not m.get("bot_id") and m.get("text")
            ]
            return "\n".join(texts)

        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Error fetching thread messages: %s", exc)
            return ""

    def verify_signature(
        self,
        timestamp: str,
        body: bytes,
        signature: str,
    ) -> bool:
        """Verify that a request came from Slack using the signing secret.

        Args:
            timestamp: X-Slack-Request-Timestamp header value.
            body: Raw request body bytes.
            signature: X-Slack-Signature header value.

        Returns:
            True if signature is valid, False otherwise.
        """
        # Reject requests older than 5 minutes to prevent replay attacks
        if abs(time.time() - int(timestamp)) > 300:
            return False

        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        computed = (
            "v0="
            + hmac.new(
                self._config.signing_secret.encode("utf-8"),
                sig_basestring.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        )
        return hmac.compare_digest(computed, signature)
