from fastapi import APIRouter

from . import create, move, stream

router = APIRouter()

router.include_router(create.router)
router.include_router(move.router)
router.include_router(stream.router)
