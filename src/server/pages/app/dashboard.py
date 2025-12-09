from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.server.deps import async_db, require_logged_in_user
from src.server.handlers import PageResponse


async def handler(
    request: Request,
    user: User = Depends(require_logged_in_user),
    db: AsyncSession = Depends(async_db),
) -> HTMLResponse:
    # Import here to avoid circular imports
    from src.database.models.game import Game

    # Get user's games
    games = await Game.get_user_games(user_id=str(user.id), session=db)

    page = PageResponse("pages/app/dashboard.html", "layouts/app.html")
    return page.render(request, {"user": user, "games": games})
