"""Tests for the chess board renderer"""

from src.chess.render import render_board_html
from src.chess.service import ChessService


class TestRenderBoard:
    def test_render_starting_position(self):
        html = render_board_html(ChessService.STARTING_FEN)

        # Should be a table
        assert '<table id="chessboard"' in html
        assert "</table>" in html

        # Should have 64 squares
        assert html.count("<td") == 64

        # Should have pieces
        assert "♔" in html  # White king
        assert "♚" in html  # Black king
        assert "♙" in html  # White pawn
        assert "♟" in html  # Black pawn

    def test_render_square_classes(self):
        html = render_board_html(ChessService.STARTING_FEN)

        # Should have light and dark squares
        assert "chess-square-light" in html
        assert "chess-square-dark" in html

    def test_render_piece_classes(self):
        html = render_board_html(ChessService.STARTING_FEN)

        # Should have piece classes
        assert "chess-piece-K" in html  # White king
        assert "chess-piece-k" in html  # Black king
        assert "chess-piece-P" in html  # White pawn
        assert "chess-piece-p" in html  # Black pawn

    def test_render_square_ids(self):
        html = render_board_html(ChessService.STARTING_FEN)

        # Should have square IDs
        assert 'id="a1"' in html
        assert 'id="e4"' in html
        assert 'id="h8"' in html

    def test_render_empty_board(self):
        # Just kings - endgame position
        fen = "8/8/8/4k3/8/8/8/4K3 w - - 0 1"
        html = render_board_html(fen)

        # Should have both kings
        assert "♔" in html
        assert "♚" in html

        # Should NOT have pawns
        assert "♙" not in html
        assert "♟" not in html
