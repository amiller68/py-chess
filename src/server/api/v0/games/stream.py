import asyncio

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from src.state import AppState

from .....deps import app_state

router = APIRouter()


@router.get("/{game_id}/stream")
async def stream_game(
    request: Request,
    game_id: str,
    state: AppState = Depends(app_state),
) -> EventSourceResponse:
    """SSE endpoint for watching game updates in real-time"""
    channel = await state.game_broadcaster.get_channel(game_id)
    queue = channel.subscribe()

    async def event_generator():
        try:
            # Send initial connection event
            yield {"event": "connected", "data": "Watching game"}

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for events with timeout for keepalive
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {"event": "keepalive", "data": ""}
        finally:
            channel.unsubscribe(queue)

    return EventSourceResponse(event_generator())
