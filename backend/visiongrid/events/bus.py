from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    DETECTION = "detection"
    ZONE_ENTER = "zone_enter"
    ZONE_EXIT = "zone_exit"
    ZONE_PRESENT = "zone_present"
    COUNT_CROSSING = "count_crossing"
    CAMERA_CONNECTED = "camera_connected"
    CAMERA_DISCONNECTED = "camera_disconnected"
    CAMERA_ERROR = "camera_error"
    ALERT = "alert"


@dataclass
class Event:
    type: EventType
    camera_name: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "camera_name": self.camera_name,
            "data": self.data,
            "timestamp": self.timestamp,
        }


EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Any]


class EventBus:
    def __init__(self, max_history: int = 1000) -> None:
        self._handlers: dict[EventType, list[EventHandler | AsyncEventHandler]] = {}
        self._global_handlers: list[EventHandler | AsyncEventHandler] = []
        self._history: list[Event] = []
        self._max_history = max_history
        self._ws_queues: list[asyncio.Queue[Event]] = []

    def subscribe(
        self, event_type: EventType, handler: EventHandler | AsyncEventHandler
    ) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler | AsyncEventHandler) -> None:
        self._global_handlers.append(handler)

    def create_ws_subscription(self) -> asyncio.Queue[Event]:
        queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=100)
        self._ws_queues.append(queue)
        return queue

    def remove_ws_subscription(self, queue: asyncio.Queue[Event]) -> None:
        self._ws_queues.remove(queue)

    def emit(self, event: Event) -> None:
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        handlers = self._handlers.get(event.type, []) + self._global_handlers
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception as e:
                logger.error("Event handler error: %s", e)

        for queue in self._ws_queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                queue.put_nowait(event)

    def get_history(
        self,
        event_type: EventType | None = None,
        camera_name: str | None = None,
        limit: int = 100,
    ) -> list[Event]:
        filtered = self._history
        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        if camera_name:
            filtered = [e for e in filtered if e.camera_name == camera_name]
        return filtered[-limit:]
