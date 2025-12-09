from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.server.deps import async_db

router = APIRouter()


@router.post("/")
async def create_game(
    db: AsyncSession = Depends(async_db),
) -> RedirectResponse:
    """Create a new game - anyone can create a game"""
    from src.database.models.game import Game

    try:
        game = await Game.create(session=db)
        await db.commit()

        return RedirectResponse(url=f"/games/{game.id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
