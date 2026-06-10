from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator

import cv2
import httpx
import numpy as np

from visiongrid.cameras.base import CameraConnector, CameraFrame, CameraStatus

logger = logging.getLogger(__name__)


class SnapshotConnector(CameraConnector):
    """Connector that polls JPEG snapshots from HTTP endpoints (Agent DVR, etc)."""

    def __init__(self, name: str, url: str, fps: int = 5) -> None:
        super().__init__(name, url, fps)
        self._client: httpx.AsyncClient | None = None
        self._running = False

    async def connect(self) -> None:
        self.status = CameraStatus.CONNECTING
        logger.info("Connecting to snapshot source: %s (%s)", self.name, self.url)

        self._client = httpx.AsyncClient(timeout=5.0)

        try:
            response = await self._client.get(self.url)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                self.status = CameraStatus.CONNECTED
                self._running = True
                logger.info("Snapshot source connected: %s", self.name)
            else:
                self.status = CameraStatus.ERROR
                raise ConnectionError(
                    f"Endpoint returned {response.status_code}, content-type: "
                    f"{response.headers.get('content-type')}"
                )
        except httpx.RequestError as e:
            self.status = CameraStatus.ERROR
            raise ConnectionError(f"Failed to connect to {self.url}: {e}")

    async def disconnect(self) -> None:
        self._running = False
        if self._client:
            await self._client.aclose()
            self._client = None
        self.status = CameraStatus.DISCONNECTED
        logger.info("Snapshot source %s disconnected", self.name)

    def is_connected(self) -> bool:
        return self._client is not None and self._running

    async def frames(self) -> AsyncIterator[CameraFrame]:
        frame_interval = 1.0 / self.target_fps

        while self._running:
            start_time = time.time()

            try:
                frame = await self._grab_frame()
                if frame is not None:
                    self._frame_count += 1
                    yield CameraFrame(
                        frame=frame,
                        camera_name=self.name,
                        frame_number=self._frame_count,
                    )
            except Exception as e:
                logger.warning("Snapshot grab failed for %s: %s", self.name, e)
                self.status = CameraStatus.RECONNECTING
                await asyncio.sleep(2.0)
                try:
                    await self.connect()
                except ConnectionError:
                    pass
                continue

            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    async def _grab_frame(self) -> np.ndarray | None:
        if self._client is None:
            return None

        response = await self._client.get(self.url)
        if response.status_code != 200:
            return None

        img_array = np.frombuffer(response.content, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
