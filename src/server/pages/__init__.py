from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import app, index

router = APIRouter()

# Home page
router.add_api_route(
    "/",
    index.handler,
    methods=["GET"],
    response_class=HTMLResponse,
)

# App routes (authenticated)
router.include_router(app.router, prefix="/app")
