from fastapi import Depends, Request
from fastapi.responses import HTMLResponse

from src.database.models import User

from ..deps import get_logged_in_user
from ..handlers import PageResponse


async def handler(
    request: Request,
    user: User | None = Depends(get_logged_in_user),
) -> HTMLResponse:
    page = PageResponse("pages/index.html", "layouts/home.html")
    return page.render(request, {"user": user})
