from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from visiongrid.detection.result import Detection


class ZoneTrigger(str, Enum):
    ENTER = "enter"
    EXIT = "exit"
    PRESENT = "present"
    ABSENT = "absent"
    LOITER = "loiter"


@dataclass
class ZoneEvent:
    zone_name: str
    camera_name: str
    trigger: ZoneTrigger
    detection: Detection
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, object]:
        return {
            "zone_name": self.zone_name,
            "camera_name": self.camera_name,
            "trigger": self.trigger.value,
            "detection": self.detection.to_dict(),
            "timestamp": self.timestamp,
        }


@dataclass
class Zone:
    name: str
    points: list[tuple[float, float]]
    triggers: list[ZoneTrigger] = field(
        default_factory=lambda: [ZoneTrigger.ENTER]
    )
    camera_name: str = ""
    classes: list[str] | None = None

    def contains_point(self, x: float, y: float) -> bool:
        polygon = np.array(self.points, dtype=np.float32)
        point = np.array([x, y], dtype=np.float32)
        result = cv2_point_in_polygon(point, polygon)
        return result


def cv2_point_in_polygon(point: np.ndarray, polygon: np.ndarray) -> bool:
    import cv2

    polygon_int = (polygon * 1000).astype(np.int32)
    point_int = tuple((point * 1000).astype(int))
    result = cv2.pointPolygonTest(polygon_int, point_int, False)
    return result >= 0


class ZoneMonitor:
    def __init__(self) -> None:
        self._zones: dict[str, Zone] = {}
        self._presence: dict[str, set[int | str]] = {}
        self._callbacks: list[callable] = []  # type: ignore[type-arg]

    def add_zone(self, zone: Zone) -> None:
        self._zones[zone.name] = zone
        self._presence[zone.name] = set()

    def remove_zone(self, name: str) -> None:
        self._zones.pop(name, None)
        self._presence.pop(name, None)

    def register_callback(self, callback: callable) -> None:  # type: ignore[type-arg]
        self._callbacks.append(callback)

    def check_detections(
        self, detections: list[Detection], camera_name: str
    ) -> list[ZoneEvent]:
        events: list[ZoneEvent] = []

        for zone in self._zones.values():
            if zone.camera_name and zone.camera_name != camera_name:
                continue

            current_in_zone: set[int | str] = set()

            for det in detections:
                if zone.classes and det.class_name not in zone.classes:
                    continue

                cx, cy = det.center
                if zone.contains_point(cx, cy):
                    det_id: int | str = det.track_id if det.track_id is not None else id(det)
                    current_in_zone.add(det_id)

                    if det_id not in self._presence[zone.name]:
                        if ZoneTrigger.ENTER in zone.triggers:
                            events.append(
                                ZoneEvent(
                                    zone_name=zone.name,
                                    camera_name=camera_name,
                                    trigger=ZoneTrigger.ENTER,
                                    detection=det,
                                )
                            )

            previous = self._presence[zone.name]
            exited = previous - current_in_zone

            if ZoneTrigger.EXIT in zone.triggers:
                for _ in exited:
                    events.append(
                        ZoneEvent(
                            zone_name=zone.name,
                            camera_name=camera_name,
                            trigger=ZoneTrigger.EXIT,
                            detection=detections[0] if detections else Detection(
                                class_name="unknown",
                                class_id=-1,
                                confidence=0,
                                bbox=(0, 0, 0, 0),
                            ),
                        )
                    )

            if ZoneTrigger.PRESENT in zone.triggers and current_in_zone:
                events.append(
                    ZoneEvent(
                        zone_name=zone.name,
                        camera_name=camera_name,
                        trigger=ZoneTrigger.PRESENT,
                        detection=detections[0],
                    )
                )

            self._presence[zone.name] = current_in_zone

        for event in events:
            for callback in self._callbacks:
                try:
                    callback(event)
                except Exception:
                    pass

        return events
