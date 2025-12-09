from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.server.deps import async_db, get_logged_in_user, require_logged_in_user
from src.server.handlers import PageResponse

router = APIRouter()


@router.get("/{game_id}", response_class=HTMLResponse)
async def view_game(
    request: Request,
    game_id: str,
    user: User | None = Depends(get_logged_in_user),
    db: AsyncSession = Depends(async_db),
) -> HTMLResponse:
    """View a game board - games are public, anyone can watch"""
    from src.chess.render import render_board_html
    from src.database.models.game import Game

    game = await Game.get_by_id(game_id=game_id, session=db)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get current position
    current_fen = await game.get_current_fen(session=db)
    board_html = render_board_html(current_fen)

    # Determine if user can move
    can_move = False
    if user and game.status in ["created", "active"]:
        from src.chess.service import ChessService

        turn = ChessService.get_turn(current_fen)
        if turn == "white" and str(game.white_player_id) == str(user.id):
            can_move = True
        elif turn == "black" and str(game.black_player_id) == str(user.id):
            can_move = True

    page = PageResponse("pages/app/game.html", "layouts/app.html")
    return page.render(
        request,
        {
            "user": user,
            "game": game,
            "board_html": board_html,
            "can_move": can_move,
            "current_fen": current_fen,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_game_form(
    request: Request,
    user: User = Depends(require_logged_in_user),
) -> HTMLResponse:
    """Show form to create a new game"""
    page = PageResponse("pages/app/new_game.html", "layouts/app.html")
    return page.render(request, {"user": user})
