from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator

import cv2
import numpy as np

from visiongrid.cameras.base import CameraConnector, CameraFrame, CameraStatus

logger = logging.getLogger(__name__)


class USBConnector(CameraConnector):
    def __init__(self, name: str, url: str, fps: int = 15) -> None:
        super().__init__(name, url, fps)
        self._cap: cv2.VideoCapture | None = None
        self._running = False

    @property
    def device_index(self) -> int:
        try:
            return int(self.url)
        except ValueError:
            return 0

    async def connect(self) -> None:
        self.status = CameraStatus.CONNECTING
        logger.info("Opening USB camera: %s (device %s)", self.name, self.url)

        loop = asyncio.get_event_loop()
        self._cap = await loop.run_in_executor(None, self._open_capture)

        if self._cap is not None and self._cap.isOpened():
            self.status = CameraStatus.CONNECTED
            self._running = True
            logger.info("USB camera %s opened successfully", self.name)
        else:
            self.status = CameraStatus.ERROR
            raise ConnectionError(f"Failed to open USB device {self.url}")

    def _open_capture(self) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(self.device_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap

    async def disconnect(self) -> None:
        self._running = False
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self.status = CameraStatus.DISCONNECTED
        logger.info("USB camera %s closed", self.name)

    def is_connected(self) -> bool:
        return self._cap is not None and self._cap.isOpened() and self._running

    async def frames(self) -> AsyncIterator[CameraFrame]:
        frame_interval = 1.0 / self.target_fps

        while self._running:
            if not self.is_connected():
                break

            start_time = time.time()
            frame = await self._read_frame()

            if frame is not None:
                self._frame_count += 1
                yield CameraFrame(
                    frame=frame,
                    camera_name=self.name,
                    frame_number=self._frame_count,
                )

                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            else:
                logger.warning("USB camera %s: failed to read frame", self.name)
                await asyncio.sleep(0.1)

    async def _read_frame(self) -> np.ndarray | None:
        if self._cap is None:
            return None
        loop = asyncio.get_event_loop()
        ret, frame = await loop.run_in_executor(None, self._cap.read)
        if not ret or frame is None:
            return None
        return frame
