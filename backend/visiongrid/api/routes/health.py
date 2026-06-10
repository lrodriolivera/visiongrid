from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> dict[str, object]:
    state = request.app.state.vg
    cameras = state.camera_manager.get_status()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "cameras": {
            "total": len(cameras),
            "connected": sum(1 for s in cameras.values() if s == "connected"),
            "status": {name: status.value for name, status in cameras.items()},
        },
    }
