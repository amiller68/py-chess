from fastapi import APIRouter

from .engine import router as engine_router
from .games import router as games_router

router = APIRouter()
router.include_router(games_router, prefix="/games", tags=["games"])
router.include_router(engine_router, prefix="/engine", tags=["engine"])
