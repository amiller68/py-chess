from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import dashboard, game

router = APIRouter()

# Dashboard (main page)
router.add_api_route(
    "/dashboard",
    dashboard.handler,
    methods=["GET"],
    response_class=HTMLResponse,
)

# Game routes
router.include_router(game.router, prefix="/games")
