from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable

import numpy as np
from ultralytics import YOLO

from visiongrid.cameras.base import CameraFrame
from visiongrid.core.config import DetectionConfig
from visiongrid.detection.result import Detection, DetectionResult

logger = logging.getLogger(__name__)

DetectionCallback = Callable[[DetectionResult], None]


class DetectionPipeline:
    def __init__(self, config: DetectionConfig) -> None:
        self.config = config
        self._model: YOLO | None = None
        self._callbacks: list[DetectionCallback] = []
        self._running = False
        self._queue: asyncio.Queue[CameraFrame] = asyncio.Queue(maxsize=100)

    def register_callback(self, callback: DetectionCallback) -> None:
        self._callbacks.append(callback)

    async def load_model(self) -> None:
        logger.info("Loading model: %s (device: %s)", self.config.model, self.config.device)
        loop = asyncio.get_event_loop()
        self._model = await loop.run_in_executor(None, self._load_model_sync)
        logger.info("Model loaded successfully: %s", self.config.model)

    def _load_model_sync(self) -> YOLO:
        model_name = self.config.model
        if not model_name.endswith(".pt"):
            model_name = f"{model_name}.pt"
        return YOLO(model_name)

    def enqueue_frame(self, frame: CameraFrame) -> None:
        try:
            self._queue.put_nowait(frame)
        except asyncio.QueueFull:
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            self._queue.put_nowait(frame)

    async def start(self) -> None:
        if self._model is None:
            await self.load_model()
        self._running = True
        logger.info("Detection pipeline started")

    async def stop(self) -> None:
        self._running = False
        logger.info("Detection pipeline stopped")

    async def run(self) -> None:
        await self.start()
        while self._running:
            try:
                frame = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                result = await self._detect(frame)
                if result.count > 0:
                    for callback in self._callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error("Detection callback error: %s", e)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Detection pipeline error: %s", e)
                await asyncio.sleep(0.1)

    async def _detect(self, frame: CameraFrame) -> DetectionResult:
        if self._model is None:
            return DetectionResult(camera_name=frame.camera_name)

        loop = asyncio.get_event_loop()
        start = time.time()

        results = await loop.run_in_executor(
            None,
            lambda: self._model.predict(  # type: ignore[union-attr]
                frame.frame,
                conf=self.config.confidence,
                classes=self._get_class_indices(),
                verbose=False,
                device=self.config.device,
            ),
        )

        inference_ms = (time.time() - start) * 1000
        detections = self._parse_results(results[0], frame.frame.shape)

        return DetectionResult(
            camera_name=frame.camera_name,
            detections=detections,
            timestamp=frame.timestamp,
            frame_number=frame.frame_number,
            inference_ms=inference_ms,
        )

    def _parse_results(
        self, result: object, frame_shape: tuple[int, ...]
    ) -> list[Detection]:
        detections: list[Detection] = []
        boxes = result.boxes  # type: ignore[attr-defined]

        if boxes is None or len(boxes) == 0:
            return detections

        h, w = frame_shape[:2]
        names = result.names  # type: ignore[attr-defined]

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = names.get(cls_id, f"class_{cls_id}")

            track_id = None
            if box.id is not None:
                track_id = int(box.id[0])

            detections.append(
                Detection(
                    class_name=class_name,
                    class_id=cls_id,
                    confidence=conf,
                    bbox=(x1 / w, y1 / h, x2 / w, y2 / h),
                    track_id=track_id,
                )
            )

        return detections

    def _get_class_indices(self) -> list[int] | None:
        if not self.config.classes:
            return None
        coco_names = self._get_coco_names()
        indices = []
        for cls_name in self.config.classes:
            if cls_name in coco_names:
                indices.append(coco_names.index(cls_name))
        return indices if indices else None

    def _get_coco_names(self) -> list[str]:
        if self._model is None:
            return []
        return list(self._model.names.values())

    async def detect_single(self, frame: np.ndarray, camera_name: str = "") -> DetectionResult:
        cam_frame = CameraFrame(frame=frame, camera_name=camera_name)
        return await self._detect(cam_frame)
