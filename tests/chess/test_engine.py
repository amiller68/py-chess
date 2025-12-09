"""Tests for the chess engine module."""

import pytest

from src.chess.engine import DummyEngine, EngineAnalysis, get_engine, shutdown_engine


class TestDummyEngine:
    """Tests for the DummyEngine implementation."""

    @pytest.fixture
    def engine(self):
        return DummyEngine(min_delay=0.01, max_delay=0.02)

    async def test_analyze_starting_position(self, engine):
        """Test analysis of starting position."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        result = await engine.analyze(fen, depth=10)

        assert isinstance(result, EngineAnalysis)
        assert -1.0 <= result.score <= 1.0
        assert len(result.best_move) >= 4  # UCI format e.g., "e2e4"
        assert result.depth == 10

    async def test_analyze_deterministic(self, engine):
        """Test that analysis is deterministic for same FEN."""
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

        result1 = await engine.analyze(fen, depth=10)
        result2 = await engine.analyze(fen, depth=10)

        assert result1.score == result2.score
        assert result1.best_move == result2.best_move

    async def test_analyze_different_positions(self, engine):
        """Test that different positions give different results."""
        fen1 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        fen2 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

        result1 = await engine.analyze(fen1)
        result2 = await engine.analyze(fen2)

        # Different positions should give different scores (very likely)
        assert result1.score != result2.score or result1.best_move != result2.best_move

    async def test_analyze_invalid_fen(self, engine):
        """Test that invalid FEN raises ValueError."""
        with pytest.raises(ValueError, match="Invalid FEN"):
            await engine.analyze("invalid fen string")

    async def test_analyze_checkmate_position(self, engine):
        """Test analysis of checkmate position (fool's mate)."""
        # White is checkmated
        fen = "rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        result = await engine.analyze(fen)

        # White is checkmated, so score should be -1.0 (black winning)
        assert result.score == -1.0
        assert result.best_move == ""  # No legal moves

    async def test_close(self, engine):
        """Test that close() doesn't raise."""
        await engine.close()


class TestEngineFactory:
    """Tests for the engine factory functions."""

    async def test_get_engine_returns_engine(self):
        """Test that get_engine returns an engine instance."""
        engine = await get_engine()
        assert engine is not None
        assert hasattr(engine, "analyze")
        assert hasattr(engine, "close")

    async def test_get_engine_singleton(self):
        """Test that get_engine returns the same instance."""
        engine1 = await get_engine()
        engine2 = await get_engine()
        assert engine1 is engine2

    async def test_shutdown_engine(self):
        """Test that shutdown_engine cleans up."""
        await get_engine()  # Ensure engine exists
        await shutdown_engine()
        # After shutdown, get_engine should create a new instance
        # (we can't easily test this without more complex setup)
