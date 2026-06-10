from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class CameraZoneConfig(BaseModel):
    name: str
    points: list[list[float]]
    triggers: list[str] = Field(default_factory=lambda: ["enter"])


class CameraAlertConfig(BaseModel):
    type: str
    notify: list[str] = Field(default_factory=list)
    cooldown: int = 60


class DetectionConfig(BaseModel):
    model: str = "yolov8n"
    confidence: float = 0.5
    classes: list[str] | None = None
    device: str = "cpu"
    batch_size: int = 1


class CameraConfig(BaseModel):
    name: str
    url: str
    protocol: str = "rtsp"
    enabled: bool = True
    fps: int = 10
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    zones: list[CameraZoneConfig] = Field(default_factory=list)
    alerts: list[CameraAlertConfig] = Field(default_factory=list)


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1


class DatabaseConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///./visiongrid.db"


class RedisConfig(BaseModel):
    url: str = "redis://localhost:6379/0"
    enabled: bool = False


class Settings(BaseSettings):
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    cameras: list[CameraConfig] = Field(default_factory=list)
    storage_path: Path = Path("./data")
    log_level: str = "INFO"

    model_config = {"env_prefix": "VISIONGRID_", "env_nested_delimiter": "__"}


def load_config(config_path: Path | None = None) -> Settings:
    if config_path and config_path.exists():
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
        return Settings(**raw)
    return Settings()
