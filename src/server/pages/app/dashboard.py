from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.server.deps import async_db
from src.server.handlers import PageResponse


async def handler(
    request: Request,
    db: AsyncSession = Depends(async_db),
) -> HTMLResponse:
    from src.database.models.game import Game

    # Get all games (public - anyone can see all games)
    games = await Game.get_all_games(session=db)

    page = PageResponse("pages/app/dashboard.html", "layouts/app.html")
    return page.render(request, {"games": games})
