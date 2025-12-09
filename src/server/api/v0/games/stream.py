import asyncio

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from src.server.deps import app_state
from src.state import AppState

router = APIRouter()


@router.get("/{game_id}/stream")
async def stream_game(
    request: Request,
    game_id: str,
    perspective: str | None = None,
    state: AppState = Depends(app_state),
) -> EventSourceResponse:
    """SSE endpoint for watching game updates in real-time.

    perspective: 'white', 'black', or None (auto-follow turn)
    """
    from src.chess.render import render_board_html
    from src.chess.service import ChessService

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
                    # Short timeout so we can check disconnect status frequently
                    # This allows faster shutdown during hot reload
                    event = await asyncio.wait_for(queue.get(), timeout=5.0)

                    # Event contains FEN - render board with client's perspective
                    if event.get("event", "").startswith("fen-update-"):
                        fen = event["data"]
                        # Use pinned perspective or follow turn
                        if perspective in ["white", "black"]:
                            view_perspective = perspective
                        else:
                            view_perspective = ChessService.get_turn(fen)

                        board_html = render_board_html(fen, perspective=view_perspective)
                        yield {
                            "event": f"game-update-{game_id}",
                            "data": board_html,
                        }
                    else:
                        yield event
                except asyncio.TimeoutError:
                    # Don't send keepalive every time - just check disconnect
                    pass
                except asyncio.CancelledError:
                    # Server is shutting down
                    break
        finally:
            channel.unsubscribe(queue)

    return EventSourceResponse(event_generator())
