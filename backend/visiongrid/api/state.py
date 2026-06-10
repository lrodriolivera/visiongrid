from __future__ import annotations

import asyncio
import logging

from visiongrid.cameras.manager import CameraManager
from visiongrid.core.config import CameraConfig, Settings
from visiongrid.detection.counter import PeopleCounter
from visiongrid.detection.pipeline import DetectionPipeline
from visiongrid.detection.result import DetectionResult
from visiongrid.detection.zones import Zone, ZoneEvent, ZoneMonitor, ZoneTrigger
from visiongrid.events.bus import Event, EventBus, EventType

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.camera_manager = CameraManager()
        self.detection_pipeline = DetectionPipeline(settings.detection)
        self.event_bus = EventBus()
        self.zone_monitor = ZoneMonitor()
        self.people_counter = PeopleCounter()
        self._detection_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        for cam_config in self.settings.cameras:
            self._setup_camera(cam_config)

        self.camera_manager.register_callback(self.detection_pipeline.enqueue_frame)

        self.detection_pipeline.register_callback(self._on_detection)
        self.zone_monitor.register_callback(self._on_zone_event)
        self.people_counter.register_callback(self._on_count_event)

        await self.detection_pipeline.load_model()
        self._detection_task = asyncio.create_task(self.detection_pipeline.run())

        await self.camera_manager.start_all()

    async def stop(self) -> None:
        await self.camera_manager.stop_all()
        await self.detection_pipeline.stop()
        if self._detection_task:
            self._detection_task.cancel()
            try:
                await self._detection_task
            except asyncio.CancelledError:
                pass

    def _setup_camera(self, config: CameraConfig) -> None:
        self.camera_manager.add_camera(config)

        for zone_cfg in config.zones:
            zone = Zone(
                name=zone_cfg.name,
                points=[tuple(p) for p in zone_cfg.points],
                triggers=[ZoneTrigger(t) for t in zone_cfg.triggers],
                camera_name=config.name,
            )
            self.zone_monitor.add_zone(zone)

    def _on_detection(self, result: DetectionResult) -> None:
        self.event_bus.emit(
            Event(
                type=EventType.DETECTION,
                camera_name=result.camera_name,
                data=result.to_dict(),
            )
        )

        zone_events = self.zone_monitor.check_detections(
            result.detections, result.camera_name
        )
        self.people_counter.update(result.detections, result.camera_name)

    def _on_zone_event(self, event: ZoneEvent) -> None:
        event_type = {
            ZoneTrigger.ENTER: EventType.ZONE_ENTER,
            ZoneTrigger.EXIT: EventType.ZONE_EXIT,
            ZoneTrigger.PRESENT: EventType.ZONE_PRESENT,
        }.get(event.trigger, EventType.ZONE_ENTER)

        self.event_bus.emit(
            Event(
                type=event_type,
                camera_name=event.camera_name,
                data=event.to_dict(),
            )
        )

    def _on_count_event(self, event: object) -> None:
        from visiongrid.detection.counter import CountEvent

        if isinstance(event, CountEvent):
            self.event_bus.emit(
                Event(
                    type=EventType.COUNT_CROSSING,
                    camera_name=event.camera_name,
                    data=event.to_dict(),
                )
            )
