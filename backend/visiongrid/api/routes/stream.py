from __future__ import annotations

import asyncio
import time
from io import BytesIO
from typing import AsyncGenerator

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from visiongrid.cameras.base import CameraFrame

router = APIRouter()


@router.get("/stream/{camera_name}")
async def stream_camera(request: Request, camera_name: str) -> StreamingResponse:
    state = request.app.state.vg
    connector = state.camera_manager.get_connector(camera_name)

    if connector is None:
        raise HTTPException(status_code=404, detail=f"Camera '{camera_name}' not found")

    if not connector.is_connected():
        raise HTTPException(status_code=503, detail=f"Camera '{camera_name}' is not connected")

    return StreamingResponse(
        _generate_mjpeg(connector),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


async def _generate_mjpeg(connector: object) -> AsyncGenerator[bytes, None]:
    frame_interval = 1.0 / 10
    max_frames = 10000

    count = 0
    async for frame in connector.frames():
        start = time.time()

        _, buffer = cv2.imencode(".jpg", frame.frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

        count += 1
        if count >= max_frames:
            break

        elapsed = time.time() - start
        sleep_time = max(0, frame_interval - elapsed)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)


@router.get("/snapshot/{camera_name}")
async def snapshot(request: Request, camera_name: str) -> StreamingResponse:
    state = request.app.state.vg
    connector = state.camera_manager.get_connector(camera_name)

    if connector is None:
        raise HTTPException(status_code=404, detail=f"Camera '{camera_name}' not found")

    if not connector.is_connected():
        raise HTTPException(status_code=503, detail=f"Camera '{camera_name}' is not connected")

    frame: CameraFrame | None = None
    async for f in connector.frames():
        frame = f
        break

    if frame is None:
        raise HTTPException(status_code=503, detail="Could not capture frame")

    _, buffer = cv2.imencode(".jpg", frame.frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return StreamingResponse(BytesIO(buffer.tobytes()), media_type="image/jpeg")
