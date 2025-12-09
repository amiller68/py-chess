from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.server.deps import async_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: AsyncSession = Depends(async_db),
) -> HTMLResponse:
    """Home page - list of all games"""
    from src.database.models.game import Game

    games = await Game.get_all_games(session=db)
    return templates.TemplateResponse("pages/index.html", {"request": request, "games": games})


@router.get("/games/new", response_class=HTMLResponse)
async def new_game_form(request: Request) -> HTMLResponse:
    """Show form to create a new game"""
    return templates.TemplateResponse("pages/new_game.html", {"request": request})


@router.get("/games/{game_id}", response_class=HTMLResponse)
async def view_game(
    request: Request,
    game_id: str,
    perspective: str | None = None,
    db: AsyncSession = Depends(async_db),
) -> HTMLResponse:
    """View a game board - anyone can view and play"""
    from src.chess.render import render_board_html
    from src.chess.service import ChessService
    from src.database.models.game import Game

    game = await Game.get_by_id(game_id=game_id, session=db)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get current position
    current_fen = await game.get_current_fen(session=db)
    turn = ChessService.get_turn(current_fen)

    # Perspective: if pinned via query param use that, otherwise follow turn
    pinned_perspective = perspective in ["white", "black"]
    view_perspective: str = perspective if pinned_perspective and perspective else turn

    board_html = render_board_html(current_fen, perspective=view_perspective)

    # Anyone can move if the game is active
    can_move = game.status in ["created", "active"]

    return templates.TemplateResponse(
        "pages/game.html",
        {
            "request": request,
            "game": game,
            "board_html": board_html,
            "can_move": can_move,
            "current_fen": current_fen,
            "turn": turn,
            "perspective": view_perspective,
            "pinned_perspective": pinned_perspective,
        },
    )
