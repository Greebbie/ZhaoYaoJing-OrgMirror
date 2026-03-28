"""Notification dispatcher that routes trigger events to handlers."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from server.triggers.event_engine import TriggerEvent

logger = logging.getLogger(__name__)

# A handler is an async callable that accepts a TriggerEvent
HandlerFn = Callable[[TriggerEvent], Coroutine[Any, Any, None]]


class NotificationDispatcher:
    """Route fired trigger events to the correct notification channel.

    Register handlers keyed by the ``visibility`` field of a rule.  When
    ``dispatch`` is called, the matching handler is invoked.  If no handler
    is registered for the event's visibility, a default handler logs the
    event.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, HandlerFn] = {}

    def register(self, visibility: str, handler: HandlerFn) -> None:
        """Register *handler* for events with the given *visibility* tag."""
        self._handlers[visibility] = handler
        logger.debug("Registered notification handler for visibility=%s", visibility)

    async def dispatch(self, event: TriggerEvent) -> None:
        """Send *event* to the handler matching its visibility."""
        handler = self._handlers.get(event.visibility, self._default_handler)
        try:
            await handler(event)
        except Exception:
            logger.exception(
                "Handler for visibility=%s failed on event rule_id=%s",
                event.visibility,
                event.rule_id,
            )

    @staticmethod
    async def _default_handler(event: TriggerEvent) -> None:
        """Fallback handler that simply logs the event."""
        logger.info(
            "Trigger fired: %s (no handler registered for visibility=%s)",
            event.rule_id,
            event.visibility,
        )
