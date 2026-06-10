from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect
from starlette.responses import Response

from visiongrid.events.bus import EventType

router = APIRouter()


@router.get("/events")
async def get_events(
    request: Request,
    type: str | None = None,
    camera: str | None = None,
    limit: int = Query(default=100, le=1000),
) -> Response:
    state = request.app.state.vg
    event_type = EventType(type) if type else None
    events = state.event_bus.get_history(
        event_type=event_type, camera_name=camera, limit=limit
    )
    data = [e.to_dict() for e in events]
    return Response(content=json.dumps(data), media_type="application/json")


@router.websocket("/ws/events")
async def websocket_events(
    websocket: WebSocket,
    type: str | None = None,
    camera: str | None = None,
) -> None:
    await websocket.accept()
    state = websocket.app.state.vg
    queue = state.event_bus.create_ws_subscription()

    try:
        while True:
            event = await queue.get()

            if type and event.type.value != type:
                continue
            if camera and event.camera_name != camera:
                continue

            await websocket.send_text(json.dumps(event.to_dict()))
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        state.event_bus.remove_ws_subscription(queue)
