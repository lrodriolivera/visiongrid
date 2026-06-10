from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from visiongrid.detection.result import Detection


@dataclass
class CountLine:
    name: str
    start: tuple[float, float]
    end: tuple[float, float]
    camera_name: str = ""
    classes: list[str] | None = None


@dataclass
class CountEvent:
    line_name: str
    camera_name: str
    direction: str  # "in" or "out"
    detection: Detection
    count_in: int
    count_out: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, object]:
        return {
            "line_name": self.line_name,
            "camera_name": self.camera_name,
            "direction": self.direction,
            "detection": self.detection.to_dict(),
            "count_in": self.count_in,
            "count_out": self.count_out,
            "timestamp": self.timestamp,
        }


class PeopleCounter:
    def __init__(self) -> None:
        self._lines: dict[str, CountLine] = {}
        self._counts: dict[str, dict[str, int]] = {}
        self._track_history: dict[str, dict[int, list[tuple[float, float]]]] = {}
        self._callbacks: list[Callable[[CountEvent], None]] = []

    def add_line(self, line: CountLine) -> None:
        self._lines[line.name] = line
        self._counts[line.name] = {"in": 0, "out": 0}
        self._track_history[line.name] = {}

    def remove_line(self, name: str) -> None:
        self._lines.pop(name, None)
        self._counts.pop(name, None)
        self._track_history.pop(name, None)

    def register_callback(self, callback: Callable[[CountEvent], None]) -> None:
        self._callbacks.append(callback)

    def get_counts(self) -> dict[str, dict[str, int]]:
        return dict(self._counts)

    def reset_counts(self, line_name: str | None = None) -> None:
        if line_name:
            self._counts[line_name] = {"in": 0, "out": 0}
        else:
            for name in self._counts:
                self._counts[name] = {"in": 0, "out": 0}

    def update(self, detections: list[Detection], camera_name: str) -> list[CountEvent]:
        events: list[CountEvent] = []

        for line in self._lines.values():
            if line.camera_name and line.camera_name != camera_name:
                continue

            for det in detections:
                if det.track_id is None:
                    continue
                if line.classes and det.class_name not in line.classes:
                    continue

                cx, cy = det.center
                history = self._track_history[line.name]

                if det.track_id not in history:
                    history[det.track_id] = []
                history[det.track_id].append((cx, cy))

                if len(history[det.track_id]) >= 2:
                    prev = history[det.track_id][-2]
                    curr = history[det.track_id][-1]
                    crossing = self._check_crossing(line, prev, curr)

                    if crossing:
                        self._counts[line.name][crossing] += 1
                        event = CountEvent(
                            line_name=line.name,
                            camera_name=camera_name,
                            direction=crossing,
                            detection=det,
                            count_in=self._counts[line.name]["in"],
                            count_out=self._counts[line.name]["out"],
                        )
                        events.append(event)
                        for callback in self._callbacks:
                            try:
                                callback(event)
                            except Exception:
                                pass
                        history[det.track_id] = [curr]

                if len(history[det.track_id]) > 30:
                    history[det.track_id] = history[det.track_id][-10:]

        self._cleanup_old_tracks()
        return events

    def _check_crossing(
        self, line: CountLine, prev: tuple[float, float], curr: tuple[float, float]
    ) -> str | None:
        d1 = self._cross_product(line.start, line.end, prev)
        d2 = self._cross_product(line.start, line.end, curr)

        if d1 * d2 < 0:
            return "in" if d2 > 0 else "out"
        return None

    @staticmethod
    def _cross_product(
        a: tuple[float, float], b: tuple[float, float], p: tuple[float, float]
    ) -> float:
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

    def _cleanup_old_tracks(self) -> None:
        for line_name in self._track_history:
            history = self._track_history[line_name]
            if len(history) > 500:
                oldest_keys = list(history.keys())[:250]
                for key in oldest_keys:
                    del history[key]
