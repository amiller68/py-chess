"""Tests for the chess service"""

from src.chess.service import ChessService


class TestChessService:
    def test_starting_fen_is_valid(self):
        assert ChessService.validate_fen(ChessService.STARTING_FEN)

    def test_invalid_fen(self):
        assert not ChessService.validate_fen("not a valid fen")

    def test_get_turn_white(self):
        # Starting position - white to move
        assert ChessService.get_turn(ChessService.STARTING_FEN) == "white"

    def test_get_turn_black(self):
        # After 1.e4 - black to move
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        assert ChessService.get_turn(fen) == "black"

    def test_make_valid_move(self):
        result = ChessService.make_move(ChessService.STARTING_FEN, "e2e4")
        assert result.success
        assert not result.is_game_over
        assert result.error is None
        assert "e4" in result.new_fen.lower() or "4P3" in result.new_fen

    def test_make_invalid_move_format(self):
        result = ChessService.make_move(ChessService.STARTING_FEN, "invalid")
        assert not result.success
        assert "Invalid UCI format" in (result.error or "")

    def test_make_illegal_move(self):
        result = ChessService.make_move(ChessService.STARTING_FEN, "e1e4")
        assert not result.success
        assert "Illegal move" in (result.error or "")

    def test_get_legal_moves(self):
        moves = ChessService.get_legal_moves(ChessService.STARTING_FEN)
        assert len(moves) == 20  # 16 pawn moves + 4 knight moves
        assert "e2e4" in moves
        assert "g1f3" in moves

    def test_checkmate_detection(self):
        # Fool's mate position - black wins
        moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
        fen = ChessService.STARTING_FEN

        for move in moves:
            result = ChessService.make_move(fen, move)
            assert result.success
            fen = result.new_fen

        # Final move should be checkmate
        assert result.is_game_over
        assert result.winner == "black"
        assert result.outcome == "checkmate"

    def test_is_check(self):
        # Position where white is in check
        fen = "rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        assert ChessService.is_check(fen)

    def test_pawn_promotion(self):
        # Position where white pawn can promote
        fen = "8/P7/8/8/8/8/8/4K2k w - - 0 1"
        result = ChessService.make_move(fen, "a7a8q")
        assert result.success
        assert "Q" in result.new_fen  # Queen on a8
