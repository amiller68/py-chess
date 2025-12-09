from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User

from .....deps import async_db, require_logged_in_user

router = APIRouter()


class CreateGameRequest(BaseModel):
    play_as: str = "white"  # "white", "black", or "random"


@router.post("")
async def create_game(
    request: CreateGameRequest,
    user: User = Depends(require_logged_in_user),
    db: AsyncSession = Depends(async_db),
) -> RedirectResponse:
    """Create a new game"""
    import random

    from src.database.models.game import Game

    # Determine player colors
    play_as = request.play_as
    if play_as == "random":
        play_as = random.choice(["white", "black"])

    white_player_id = str(user.id) if play_as == "white" else None
    black_player_id = str(user.id) if play_as == "black" else None

    try:
        game = await Game.create(
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            session=db,
        )
        await db.commit()

        return RedirectResponse(url=f"/app/games/{game.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
