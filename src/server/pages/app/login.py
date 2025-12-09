from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse

from src.database.models import User
from src.server.deps import get_logged_in_user
from src.server.handlers import PageResponse


async def handler(
    request: Request,
    user: User | None = Depends(get_logged_in_user),
) -> Response:
    # If already logged in, redirect to dashboard
    if user:
        return RedirectResponse(url="/app/dashboard", status_code=302)

    page = PageResponse("pages/app/login.html", "layouts/minimal.html")
    return page.render(request, {})
