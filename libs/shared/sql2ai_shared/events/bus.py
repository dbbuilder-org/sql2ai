"""Event bus for publishing and subscribing to domain events."""

from typing import Callable, Dict, List, Any, Awaitable
from collections import defaultdict
import asyncio
import structlog

from sql2ai_shared.events.types import DomainEvent

logger = structlog.get_logger()

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """In-process event bus with async support.

    Supports:
    - Multiple handlers per event type
    - Wildcard subscriptions (*)
    - Async handlers
    - Error isolation (one handler failure doesn't affect others)

    Usage:
        bus = EventBus()

        @bus.subscribe("query.executed")
        async def on_query_executed(event: QueryExecutedEvent):
            await log_query(event)

        await bus.publish(QueryExecutedEvent(...))
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._middleware: List[Callable] = []

    def subscribe(
        self, event_type: str
    ) -> Callable[[EventHandler], EventHandler]:
        """Decorator for subscribing to events.

        Args:
            event_type: Event type to subscribe to, or "*" for all events

        Usage:
            @bus.subscribe("query.executed")
            async def handler(event):
                pass
        """

        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers[event_type].append(handler)
            logger.debug(
                "event_handler_registered",
                event_type=event_type,
                handler=handler.__name__,
            )
            return handler

        return decorator

    def add_handler(self, event_type: str, handler: EventHandler) -> None:
        """Add a handler programmatically."""
        self._handlers[event_type].append(handler)

    def remove_handler(self, event_type: str, handler: EventHandler) -> None:
        """Remove a handler."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def add_middleware(
        self, middleware: Callable[[DomainEvent, Callable], Awaitable[None]]
    ) -> None:
        """Add middleware that runs before handlers.

        Middleware signature: async def middleware(event, next) -> None
        """
        self._middleware.append(middleware)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers.

        Handlers are called concurrently. Errors in one handler
        don't affect others.
        """
        logger.info(
            "event_published",
            event_type=event.event_type,
            event_id=event.event_id,
            tenant_id=event.tenant_id,
        )

        # Get handlers for specific event type and wildcard
        handlers = (
            self._handlers.get(event.event_type, [])
            + self._handlers.get("*", [])
        )

        if not handlers:
            return

        # Run handlers concurrently
        tasks = [
            self._run_handler(handler, event)
            for handler in handlers
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_handler(
        self, handler: EventHandler, event: DomainEvent
    ) -> None:
        """Run a single handler with error isolation."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                "event_handler_error",
                event_type=event.event_type,
                event_id=event.event_id,
                handler=handler.__name__,
                error=str(e),
                exc_info=True,
            )

    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        for event in events:
            await self.publish(event)

    def handler_count(self, event_type: str | None = None) -> int:
        """Get the number of handlers for an event type."""
        if event_type:
            return len(self._handlers.get(event_type, []))
        return sum(len(handlers) for handlers in self._handlers.values())


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def set_event_bus(bus: EventBus) -> None:
    """Set the global event bus instance (for testing)."""
    global _event_bus
    _event_bus = bus


# Convenience function
async def publish(event: DomainEvent) -> None:
    """Publish an event to the global event bus."""
    await get_event_bus().publish(event)
