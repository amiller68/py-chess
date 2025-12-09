from fastapi import Request
from fastapi.responses import HTMLResponse

from src.server.handlers import PageResponse


async def handler(request: Request) -> HTMLResponse:
    page = PageResponse("pages/index.html", "layouts/home.html")
    return page.render(request, {})
