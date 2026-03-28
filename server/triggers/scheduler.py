"""Periodic trigger evaluation scheduler."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.notifications.dispatcher import NotificationDispatcher
    from server.triggers.event_engine import EventEngine, TriggerEvent

logger = logging.getLogger(__name__)

_DEFAULT_INTERVAL_SECONDS = 300  # 5 minutes


class TriggerScheduler:
    """Run the trigger engine on a fixed interval and dispatch results.

    Args:
        engine: The ``EventEngine`` that evaluates rules.
        dispatcher: The ``NotificationDispatcher`` to route fired events.
        interval_seconds: Seconds between evaluation cycles (default 300).
    """

    def __init__(
        self,
        engine: EventEngine,
        dispatcher: NotificationDispatcher,
        interval_seconds: int = _DEFAULT_INTERVAL_SECONDS,
    ) -> None:
        self.engine = engine
        self.dispatcher = dispatcher
        self.interval = interval_seconds
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Begin the periodic evaluation loop in the background."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "TriggerScheduler started (interval=%ds)", self.interval
        )

    async def stop(self) -> None:
        """Gracefully stop the evaluation loop."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("TriggerScheduler stopped")

    async def _run_loop(self) -> None:
        """Internal loop that evaluates and dispatches on each tick."""
        while self._running:
            try:
                events = await self.engine.evaluate_all()
                logger.info("Trigger evaluation produced %d event(s)", len(events))
                for event in events:
                    await self.dispatcher.dispatch(event)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Trigger evaluation failed")
            await asyncio.sleep(self.interval)

    async def run_once(self) -> list[TriggerEvent]:
        """Manually evaluate all rules once (e.g. from an API endpoint).

        Returns:
            The list of fired ``TriggerEvent`` objects.
        """
        events = await self.engine.evaluate_all()
        for event in events:
            await self.dispatcher.dispatch(event)
        return events
