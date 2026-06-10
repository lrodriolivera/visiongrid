from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Detection:
    class_name: str
    class_id: int
    confidence: float
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized 0-1)
    track_id: int | None = None

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

    def to_dict(self) -> dict[str, object]:
        return {
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": round(self.confidence, 3),
            "bbox": [round(v, 4) for v in self.bbox],
            "track_id": self.track_id,
            "center": [round(v, 4) for v in self.center],
        }


@dataclass
class DetectionResult:
    camera_name: str
    detections: list[Detection] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    frame_number: int = 0
    inference_ms: float = 0.0

    @property
    def count(self) -> int:
        return len(self.detections)

    def by_class(self, class_name: str) -> list[Detection]:
        return [d for d in self.detections if d.class_name == class_name]

    def to_dict(self) -> dict[str, object]:
        return {
            "camera_name": self.camera_name,
            "timestamp": self.timestamp,
            "frame_number": self.frame_number,
            "inference_ms": round(self.inference_ms, 2),
            "count": self.count,
            "detections": [d.to_dict() for d in self.detections],
        }
