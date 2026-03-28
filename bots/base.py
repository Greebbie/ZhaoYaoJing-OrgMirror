"""Abstract base class for all bot platform integrations."""

from abc import ABC, abstractmethod
from typing import Any


class BaseBotHandler(ABC):
    """Abstract base class for all bot integrations.

    Each platform (Feishu, Slack, WeCom, etc.) implements this interface
    to provide a thin client that forwards messages to the core API.
    """

    platform: str = "base"

    @abstractmethod
    async def on_message(self, event: dict[str, Any]) -> None:
        """Handle incoming message."""
        ...

    @abstractmethod
    async def on_mention(self, event: dict[str, Any]) -> None:
        """Handle @mention."""
        ...

    @abstractmethod
    async def on_command(self, command: str, args: str, event: dict[str, Any]) -> None:
        """Handle bot command (e.g. @bot scan)."""
        ...

    @abstractmethod
    async def send_reply(
        self, channel_id: str, content: Any, reply_to: str | None = None
    ) -> None:
        """Send a reply to a channel/group."""
        ...

    @abstractmethod
    async def send_private(self, user_id: str, content: Any) -> None:
        """Send a private/DM message."""
        ...

    def parse_command(self, text: str) -> tuple[str, str]:
        """Parse command from text. Returns (command, remaining_args).

        Supported commands:
        - scan (default): analyze content through the mirror pipeline
        - xray: extract actionable items from a requirement
        - retro: generate a retrospective analysis (placeholder)
        - weekly: generate a weekly report (placeholder)
        - self-check: self-mirror analysis for the sender's own text
        """
        commands = ["scan", "xray", "retro", "weekly", "self-check"]
        text = text.strip()
        for cmd in commands:
            if text.startswith(cmd):
                return cmd, text[len(cmd):].strip()
        return "scan", text  # Default to scan
