"""Chess engine abstraction and dummy implementation.

This module provides a scaffold for integrating chess engines into the application.
The current implementation uses a dummy engine for development/demo purposes.

TODO: To integrate a real engine (e.g., Stockfish):
1. Install stockfish binary and add path to your config
2. Create a new class (e.g., StockfishEngine) implementing the ChessEngine protocol
3. Use chess.engine.SimpleEngine.popen_uci() for UCI communication:

   import chess.engine

   class StockfishEngine:
       def __init__(self, path: str = "/usr/local/bin/stockfish"):
           self._engine = chess.engine.SimpleEngine.popen_uci(path)

       async def analyze(self, fen: str, depth: int = 10) -> EngineAnalysis:
           board = chess.Board(fen)
           info = await self._engine.analyse(board, chess.engine.Limit(depth=depth))

           # Convert centipawn score to [-1, 1] range
           cp = info["score"].relative.score(mate_score=10000)
           score = math.tanh(cp / 1000)  # Sigmoid-like compression

           best_move = info["pv"][0].uci() if info.get("pv") else ""
           return EngineAnalysis(score=score, best_move=best_move, depth=depth)

       async def close(self) -> None:
           self._engine.quit()

4. Update get_engine() to return your engine based on configuration
"""

import asyncio
import hashlib
import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import chess


@dataclass(frozen=True)
class EngineAnalysis:
    """Result of engine position analysis.

    Attributes:
        score: Position evaluation from -1.0 (black winning) to 1.0 (white winning).
               0.0 is equal. Values are clamped to this range.
        best_move: Best move in UCI format (e.g., "e2e4"). Empty string if no move.
        depth: Search depth used for analysis.
    """

    score: float
    best_move: str
    depth: int


@runtime_checkable
class ChessEngine(Protocol):
    """Protocol defining the chess engine interface.

    Any chess engine implementation must provide this interface.
    The protocol allows for async operations since real engines
    may take variable time to compute.

    TODO: Real engine implementations should:
    - Handle engine process lifecycle (start/stop)
    - Implement proper resource cleanup in close()
    - Handle timeouts gracefully
    - Consider caching results for repeated positions
    """

    async def analyze(self, fen: str, depth: int = 10) -> EngineAnalysis:
        """Analyze a chess position.

        Args:
            fen: FEN string of the position to analyze.
            depth: Search depth (higher = stronger but slower).

        Returns:
            EngineAnalysis with score and best move.

        Raises:
            ValueError: If FEN is invalid.
        """
        ...

    async def close(self) -> None:
        """Clean up engine resources.

        Called during application shutdown.
        Real engines should terminate subprocess here.
        """
        ...


class DummyEngine:
    """Dummy engine that returns deterministic results based on FEN hashing.

    This implementation provides:
    - Score: MD5 hash of FEN mapped to [-1, 1] range
    - Best move: Random legal move (seeded by FEN hash for consistency)
    - Simulated delay to test async behavior

    TODO: Replace this with a real engine implementation.
    See module docstring for integration guide.
    """

    def __init__(self, min_delay: float = 0.1, max_delay: float = 0.3):
        """Initialize dummy engine.

        Args:
            min_delay: Minimum simulated thinking time in seconds.
            max_delay: Maximum simulated thinking time in seconds.
        """
        self._min_delay = min_delay
        self._max_delay = max_delay

    async def analyze(self, fen: str, depth: int = 10) -> EngineAnalysis:
        """Analyze position with dummy evaluation.

        Score is derived from FEN hash (deterministic but varied).
        Best move is a random legal move (seeded for consistency).
        """
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {e}") from e

        # Generate deterministic hash from FEN
        fen_hash = hashlib.md5(fen.encode()).hexdigest()
        hash_value = int(fen_hash[:8], 16)

        # Simulate variable thinking time based on depth
        # TODO: Remove this delay when using a real engine
        delay = self._min_delay + (hash_value % 1000) / 1000 * (
            self._max_delay - self._min_delay
        )
        delay *= 1 + depth * 0.02  # Slightly longer for higher depth
        await asyncio.sleep(delay)

        # Handle game over positions
        if board.is_game_over():
            outcome = board.outcome()
            if outcome and outcome.winner == chess.WHITE:
                return EngineAnalysis(score=1.0, best_move="", depth=depth)
            elif outcome and outcome.winner == chess.BLACK:
                return EngineAnalysis(score=-1.0, best_move="", depth=depth)
            else:
                return EngineAnalysis(score=0.0, best_move="", depth=depth)

        # Generate deterministic score from FEN hash
        # Maps hash to [-0.6, 0.6] range (most positions are roughly equal)
        # TODO: Replace with real engine evaluation
        raw_score = (hash_value / 0xFFFFFFFF) * 2 - 1  # [-1, 1]
        score = raw_score * 0.6  # Compress to [-0.6, 0.6]

        # Pick random legal move (seeded by FEN for determinism)
        # TODO: Replace with real engine best move
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return EngineAnalysis(score=score, best_move="", depth=depth)

        rng = random.Random(hash_value)
        best_move = rng.choice(legal_moves).uci()

        return EngineAnalysis(score=round(score, 3), best_move=best_move, depth=depth)

    async def close(self) -> None:
        """No cleanup needed for dummy engine."""
        pass


# Global engine instance (singleton pattern)
_engine_instance: ChessEngine | None = None


async def get_engine() -> ChessEngine:
    """Get or create the chess engine instance.

    Uses singleton pattern to reuse engine across requests.

    TODO: To use a different engine:
    1. Add engine configuration (e.g., CHESS_ENGINE_TYPE env var)
    2. Check config here and instantiate the appropriate engine:

       if config.engine_type == "stockfish":
           return StockfishEngine(config.stockfish_path)

    Returns:
        ChessEngine instance ready for analysis.
    """
    global _engine_instance

    if _engine_instance is None:
        # TODO: Check configuration to select real engine
        _engine_instance = DummyEngine()

    return _engine_instance


async def shutdown_engine() -> None:
    """Shutdown engine during app cleanup.

    Call this from application shutdown to properly release resources.
    """
    global _engine_instance

    if _engine_instance is not None:
        await _engine_instance.close()
        _engine_instance = None
