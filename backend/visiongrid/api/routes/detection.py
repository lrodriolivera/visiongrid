from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ZoneCreate(BaseModel):
    name: str
    camera_name: str
    points: list[list[float]]
    triggers: list[str] = ["enter"]
    classes: list[str] | None = None


class CountLineCreate(BaseModel):
    name: str
    camera_name: str
    start: list[float]
    end: list[float]
    classes: list[str] | None = None


@router.get("/detection/status")
async def detection_status(request: Request) -> dict[str, object]:
    state = request.app.state.vg
    pipeline = state.detection_pipeline
    return {
        "model": state.settings.detection.model,
        "device": state.settings.detection.device,
        "running": pipeline._running,
        "queue_size": pipeline._queue.qsize(),
    }


@router.get("/zones")
async def list_zones(request: Request) -> list[dict[str, object]]:
    state = request.app.state.vg
    zones = state.zone_monitor._zones
    return [
        {
            "name": z.name,
            "camera_name": z.camera_name,
            "points": [list(p) for p in z.points],
            "triggers": [t.value for t in z.triggers],
        }
        for z in zones.values()
    ]


@router.post("/zones", status_code=201)
async def create_zone(request: Request, zone: ZoneCreate) -> dict[str, object]:
    from visiongrid.detection.zones import Zone, ZoneTrigger

    state = request.app.state.vg
    new_zone = Zone(
        name=zone.name,
        points=[tuple(p) for p in zone.points],
        triggers=[ZoneTrigger(t) for t in zone.triggers],
        camera_name=zone.camera_name,
        classes=zone.classes,
    )
    state.zone_monitor.add_zone(new_zone)
    return {"status": "created", "name": zone.name}


@router.delete("/zones/{name}")
async def delete_zone(request: Request, name: str) -> dict[str, str]:
    state = request.app.state.vg
    state.zone_monitor.remove_zone(name)
    return {"status": "removed", "name": name}


@router.get("/counting")
async def get_counts(request: Request) -> dict[str, object]:
    state = request.app.state.vg
    return {"counts": state.people_counter.get_counts()}


@router.post("/counting/lines", status_code=201)
async def create_count_line(request: Request, line: CountLineCreate) -> dict[str, object]:
    from visiongrid.detection.counter import CountLine

    state = request.app.state.vg
    new_line = CountLine(
        name=line.name,
        start=tuple(line.start),
        end=tuple(line.end),
        camera_name=line.camera_name,
        classes=line.classes,
    )
    state.people_counter.add_line(new_line)
    return {"status": "created", "name": line.name}


@router.post("/counting/reset")
async def reset_counts(request: Request, line_name: str | None = None) -> dict[str, str]:
    state = request.app.state.vg
    state.people_counter.reset_counts(line_name)
    return {"status": "reset"}
