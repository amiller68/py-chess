from fastapi import APIRouter

from .auth import router as auth_router
from .games import router as games_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(games_router, prefix="/games", tags=["games"])
