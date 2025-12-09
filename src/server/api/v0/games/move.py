from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.state import AppState

from .....deps import app_state, async_db, require_logged_in_user

router = APIRouter()


@router.post("/{game_id}/move")
async def make_move(
    request: Request,
    game_id: str,
    uci_move: str = Form(alias="uciMove"),
    resign: bool = Form(default=False),
    user: User = Depends(require_logged_in_user),
    db: AsyncSession = Depends(async_db),
    state: AppState = Depends(app_state),
) -> Response:
    """Submit a move for a game"""
    from src.chess.render import render_board_html
    from src.chess.service import ChessService
    from src.database.models.game import Game

    game = await Game.get_by_id(game_id=game_id, session=db)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status == "complete":
        raise HTTPException(status_code=400, detail="Game is already complete")

    # Get current position
    current_fen = await game.get_current_fen(session=db)

    # Validate it's the user's turn
    turn = ChessService.get_turn(current_fen)
    if turn == "white" and str(game.white_player_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not your turn")
    elif turn == "black" and str(game.black_player_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not your turn")

    # Handle resignation
    if resign:
        winner = "black" if turn == "white" else "white"
        await Game.complete_game(
            game_id=game_id,
            winner=winner,
            outcome="resignation",
            session=db,
        )
        await db.commit()

        # Broadcast update
        new_board_html = render_board_html(current_fen)
        await state.game_broadcaster.broadcast_to_game(game_id, new_board_html)

        return Response(status_code=200)

    # Validate and apply move
    result = ChessService.make_move(current_fen, uci_move)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error or "Invalid move")

    # Record the move
    await Game.record_move(
        game_id=game_id,
        uci_move=uci_move,
        new_fen=result.new_fen,
        session=db,
    )

    # Check for game over
    if result.is_game_over:
        await Game.complete_game(
            game_id=game_id,
            winner=result.winner,
            outcome=result.outcome,
            session=db,
        )

    await db.commit()

    # Broadcast update to all watchers
    new_board_html = render_board_html(result.new_fen)
    await state.game_broadcaster.broadcast_to_game(game_id, new_board_html)

    return Response(status_code=200)
