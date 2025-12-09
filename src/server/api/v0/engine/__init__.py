"""Engine analysis API endpoints.

Provides endpoints for chess position analysis using the configured engine.

TODO: For production with a real engine:
- Add rate limiting to prevent abuse (e.g., slowapi)
- Consider caching results for repeated positions
- Add timeout handling for long-running analysis
- Consider WebSocket endpoint for real-time updates during analysis
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.chess.engine import get_engine
from src.chess.service import ChessService

router = APIRouter()


class AnalyzeResponse(BaseModel):
    """Response from engine analysis.

    Attributes:
        score: Position evaluation from -1.0 (black winning) to 1.0 (white winning).
        best_move: Best move in UCI notation (e.g., "e2e4").
        depth: Search depth used for analysis.
    """

    score: float
    best_move: str
    depth: int


@router.get("/analyze")
async def analyze_position(
    fen: str = Query(..., description="FEN string of position to analyze"),
    depth: int = Query(default=10, ge=1, le=30, description="Search depth (1-30)"),
) -> AnalyzeResponse:
    """Analyze a chess position and return evaluation.

    Returns:
        - score: Position evaluation from -1.0 (black winning) to 1.0 (white winning)
        - best_move: Best move in UCI notation
        - depth: Search depth used

    Raises:
        400: Invalid FEN string
        500: Engine analysis failed

    TODO: Consider adding:
    - Request cancellation support
    - Position caching
    - Rate limiting per client
    """
    # Validate FEN
    if not ChessService.validate_fen(fen):
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    try:
        engine = await get_engine()
        result = await engine.analyze(fen, depth)

        return AnalyzeResponse(
            score=result.score,
            best_move=result.best_move,
            depth=result.depth,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine analysis failed: {e}")
