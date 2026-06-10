from __future__ import annotations

import asyncio
import logging
from typing import Callable

from visiongrid.cameras.base import CameraConnector, CameraFrame, CameraStatus
from visiongrid.cameras.http import HTTPConnector
from visiongrid.cameras.rtsp import RTSPConnector
from visiongrid.cameras.snapshot import SnapshotConnector
from visiongrid.cameras.usb import USBConnector
from visiongrid.core.config import CameraConfig

logger = logging.getLogger(__name__)

PROTOCOL_MAP: dict[str, type[CameraConnector]] = {
    "rtsp": RTSPConnector,
    "rtmp": RTSPConnector,
    "http": HTTPConnector,
    "https": HTTPConnector,
    "mjpeg": HTTPConnector,
    "hls": HTTPConnector,
    "usb": USBConnector,
    "v4l2": USBConnector,
    "snapshot": SnapshotConnector,
    "jpeg": SnapshotConnector,
}

FrameCallback = Callable[[CameraFrame], None]


class CameraManager:
    def __init__(self) -> None:
        self._connectors: dict[str, CameraConnector] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._callbacks: list[FrameCallback] = []

    def register_callback(self, callback: FrameCallback) -> None:
        self._callbacks.append(callback)

    def add_camera(self, config: CameraConfig) -> CameraConnector:
        protocol = config.protocol.lower()
        connector_cls = PROTOCOL_MAP.get(protocol)

        if connector_cls is None:
            raise ValueError(f"Unsupported protocol: {protocol}")

        connector = connector_cls(
            name=config.name,
            url=config.url,
            fps=config.fps,
        )
        self._connectors[config.name] = connector
        logger.info("Camera added: %s (%s via %s)", config.name, config.url, protocol)
        return connector

    def remove_camera(self, name: str) -> None:
        if name in self._tasks:
            self._tasks[name].cancel()
            del self._tasks[name]
        if name in self._connectors:
            del self._connectors[name]
            logger.info("Camera removed: %s", name)

    async def start_camera(self, name: str) -> None:
        connector = self._connectors.get(name)
        if connector is None:
            raise ValueError(f"Camera not found: {name}")

        await connector.connect()
        task = asyncio.create_task(self._run_camera(connector))
        self._tasks[name] = task

    async def stop_camera(self, name: str) -> None:
        if name in self._tasks:
            self._tasks[name].cancel()
            try:
                await self._tasks[name]
            except asyncio.CancelledError:
                pass
            del self._tasks[name]

        connector = self._connectors.get(name)
        if connector:
            await connector.disconnect()

    async def start_all(self) -> None:
        for name in self._connectors:
            try:
                await self.start_camera(name)
            except ConnectionError as e:
                logger.error("Failed to start camera %s: %s", name, e)

    async def stop_all(self) -> None:
        for name in list(self._tasks.keys()):
            await self.stop_camera(name)

    def get_status(self) -> dict[str, CameraStatus]:
        return {name: conn.status for name, conn in self._connectors.items()}

    def get_connector(self, name: str) -> CameraConnector | None:
        return self._connectors.get(name)

    @property
    def cameras(self) -> dict[str, CameraConnector]:
        return dict(self._connectors)

    async def _run_camera(self, connector: CameraConnector) -> None:
        try:
            async for frame in connector.frames():
                for callback in self._callbacks:
                    try:
                        callback(frame)
                    except Exception as e:
                        logger.error(
                            "Frame callback error for %s: %s", connector.name, e
                        )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Camera %s stream error: %s", connector.name, e)
            connector.status = CameraStatus.ERROR
