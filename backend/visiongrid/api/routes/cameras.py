from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from visiongrid.core.config import CameraConfig, DetectionConfig

router = APIRouter()


class CameraCreate(BaseModel):
    name: str
    url: str
    protocol: str = "rtsp"
    fps: int = 10
    enabled: bool = True
    detection: DetectionConfig | None = None


class CameraResponse(BaseModel):
    name: str
    url: str
    protocol: str
    fps: int
    enabled: bool
    status: str


@router.get("/cameras")
async def list_cameras(request: Request) -> list[CameraResponse]:
    state = request.app.state.vg
    cameras = state.camera_manager.cameras
    statuses = state.camera_manager.get_status()

    return [
        CameraResponse(
            name=name,
            url=conn.url,
            protocol=type(conn).__name__.replace("Connector", "").lower(),
            fps=conn.target_fps,
            enabled=True,
            status=statuses.get(name, "unknown").value
            if hasattr(statuses.get(name), "value")
            else "unknown",
        )
        for name, conn in cameras.items()
    ]


@router.post("/cameras", status_code=201)
async def add_camera(request: Request, camera: CameraCreate) -> CameraResponse:
    state = request.app.state.vg

    if camera.name in state.camera_manager.cameras:
        raise HTTPException(status_code=409, detail=f"Camera '{camera.name}' already exists")

    config = CameraConfig(
        name=camera.name,
        url=camera.url,
        protocol=camera.protocol,
        fps=camera.fps,
        enabled=camera.enabled,
        detection=camera.detection or state.settings.detection,
    )

    try:
        state.camera_manager.add_camera(config)
        if camera.enabled:
            await state.camera_manager.start_camera(camera.name)
    except (ValueError, ConnectionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    statuses = state.camera_manager.get_status()
    return CameraResponse(
        name=camera.name,
        url=camera.url,
        protocol=camera.protocol,
        fps=camera.fps,
        enabled=camera.enabled,
        status=statuses.get(camera.name, "unknown").value,
    )


@router.delete("/cameras/{name}")
async def remove_camera(request: Request, name: str) -> dict[str, str]:
    state = request.app.state.vg

    if name not in state.camera_manager.cameras:
        raise HTTPException(status_code=404, detail=f"Camera '{name}' not found")

    await state.camera_manager.stop_camera(name)
    state.camera_manager.remove_camera(name)
    return {"status": "removed", "name": name}


@router.post("/cameras/{name}/start")
async def start_camera(request: Request, name: str) -> dict[str, str]:
    state = request.app.state.vg

    if name not in state.camera_manager.cameras:
        raise HTTPException(status_code=404, detail=f"Camera '{name}' not found")

    try:
        await state.camera_manager.start_camera(name)
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"status": "started", "name": name}


@router.post("/cameras/{name}/stop")
async def stop_camera(request: Request, name: str) -> dict[str, str]:
    state = request.app.state.vg

    if name not in state.camera_manager.cameras:
        raise HTTPException(status_code=404, detail=f"Camera '{name}' not found")

    await state.camera_manager.stop_camera(name)
    return {"status": "stopped", "name": name}
