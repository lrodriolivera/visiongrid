from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator

import numpy as np


class CameraStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class CameraFrame:
    frame: np.ndarray
    timestamp: float = field(default_factory=time.time)
    camera_name: str = ""
    frame_number: int = 0
    width: int = 0
    height: int = 0

    def __post_init__(self) -> None:
        if self.width == 0 and self.frame is not None:
            self.height, self.width = self.frame.shape[:2]


class CameraConnector(ABC):
    def __init__(self, name: str, url: str, fps: int = 10) -> None:
        self.name = name
        self.url = url
        self.target_fps = fps
        self.status = CameraStatus.DISCONNECTED
        self._frame_count = 0

    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def frames(self) -> AsyncIterator[CameraFrame]:
        ...
        yield  # type: ignore[misc]

    @abstractmethod
    def is_connected(self) -> bool:
        ...

    @property
    def frame_count(self) -> int:
        return self._frame_count
