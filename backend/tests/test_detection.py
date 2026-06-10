from __future__ import annotations

import numpy as np
import pytest

from visiongrid.detection.counter import CountLine, PeopleCounter
from visiongrid.detection.result import Detection, DetectionResult
from visiongrid.detection.zones import Zone, ZoneMonitor, ZoneTrigger


class TestDetection:
    def test_detection_creation(self) -> None:
        det = Detection(
            class_name="person",
            class_id=0,
            confidence=0.95,
            bbox=(0.1, 0.2, 0.3, 0.4),
        )
        assert det.class_name == "person"
        assert det.confidence == 0.95
        assert det.center == pytest.approx((0.2, 0.3))
        assert det.area == pytest.approx(0.04)

    def test_detection_result(self) -> None:
        detections = [
            Detection("person", 0, 0.9, (0.1, 0.1, 0.3, 0.3)),
            Detection("car", 2, 0.8, (0.5, 0.5, 0.9, 0.9)),
            Detection("person", 0, 0.7, (0.2, 0.2, 0.4, 0.4)),
        ]
        result = DetectionResult(
            camera_name="test",
            detections=detections,
            frame_number=1,
        )
        assert result.count == 3
        assert len(result.by_class("person")) == 2
        assert len(result.by_class("car")) == 1

    def test_detection_to_dict(self) -> None:
        det = Detection("dog", 16, 0.85, (0.1, 0.2, 0.5, 0.6))
        d = det.to_dict()
        assert d["class_name"] == "dog"
        assert d["confidence"] == 0.85
        assert len(d["bbox"]) == 4


class TestZoneMonitor:
    def test_zone_contains_point(self) -> None:
        zone = Zone(
            name="test_zone",
            points=[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)],
            triggers=[ZoneTrigger.ENTER],
        )
        assert zone.contains_point(0.5, 0.5) is True
        assert zone.contains_point(0.1, 0.1) is False

    def test_zone_enter_event(self) -> None:
        monitor = ZoneMonitor()
        zone = Zone(
            name="entrance",
            points=[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)],
            triggers=[ZoneTrigger.ENTER],
            camera_name="cam1",
        )
        monitor.add_zone(zone)

        detections = [
            Detection("person", 0, 0.9, (0.3, 0.3, 0.5, 0.5), track_id=1),
        ]
        events = monitor.check_detections(detections, "cam1")
        assert len(events) == 1
        assert events[0].trigger == ZoneTrigger.ENTER

        events = monitor.check_detections(detections, "cam1")
        assert len(events) == 0


class TestPeopleCounter:
    def test_line_crossing(self) -> None:
        counter = PeopleCounter()
        line = CountLine(
            name="door",
            start=(0.5, 0.0),
            end=(0.5, 1.0),
            camera_name="cam1",
        )
        counter.add_line(line)

        det1 = Detection("person", 0, 0.9, (0.2, 0.4, 0.4, 0.6), track_id=1)
        counter.update([det1], "cam1")

        det2 = Detection("person", 0, 0.9, (0.6, 0.4, 0.8, 0.6), track_id=1)
        events = counter.update([det2], "cam1")

        assert len(events) == 1
        counts = counter.get_counts()
        assert counts["door"]["in"] + counts["door"]["out"] == 1

    def test_reset_counts(self) -> None:
        counter = PeopleCounter()
        line = CountLine(name="gate", start=(0.5, 0.0), end=(0.5, 1.0))
        counter.add_line(line)
        counter._counts["gate"] = {"in": 5, "out": 3}

        counter.reset_counts("gate")
        assert counter.get_counts()["gate"] == {"in": 0, "out": 0}
