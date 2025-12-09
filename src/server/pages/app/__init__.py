from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import dashboard, game, login

router = APIRouter()

# Login page (unauthenticated)
router.add_api_route(
    "/login",
    login.handler,
    methods=["GET"],
    response_class=HTMLResponse,
)

# Dashboard (authenticated)
router.add_api_route(
    "/dashboard",
    dashboard.handler,
    methods=["GET"],
    response_class=HTMLResponse,
)

# Game routes
router.include_router(game.router, prefix="/games")
