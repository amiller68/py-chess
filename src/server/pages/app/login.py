from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.database.models import User

from ...deps import get_logged_in_user
from ...handlers import PageResponse


async def handler(
    request: Request,
    user: User | None = Depends(get_logged_in_user),
) -> HTMLResponse | RedirectResponse:
    # If already logged in, redirect to dashboard
    if user:
        return RedirectResponse(url="/app/dashboard", status_code=302)

    page = PageResponse("pages/app/login.html", "layouts/minimal.html")
    return page.render(request, {})
