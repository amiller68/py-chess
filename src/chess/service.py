"""Chess game logic service using python-chess library"""

from dataclasses import dataclass
from typing import Optional

import chess


@dataclass
class MoveResult:
    """Result of attempting to make a move"""

    success: bool
    new_fen: str
    is_game_over: bool
    winner: Optional[str] = None  # "white", "black", "draw"
    outcome: Optional[str] = None  # "checkmate", "stalemate", etc.
    error: Optional[str] = None


class ChessService:
    """Wrapper around python-chess for game logic"""

    STARTING_FEN = chess.STARTING_FEN

    @staticmethod
    def validate_fen(fen: str) -> bool:
        """Check if a FEN string is valid"""
        try:
            chess.Board(fen)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_turn(fen: str) -> str:
        """Get whose turn it is from a FEN (returns 'white' or 'black')"""
        board = chess.Board(fen)
        return "white" if board.turn == chess.WHITE else "black"

    @staticmethod
    def make_move(fen: str, uci_move: str) -> MoveResult:
        """
        Attempt to make a move on the board.
        Returns MoveResult with success/failure and new state.
        """
        board = chess.Board(fen)

        # Parse UCI move
        try:
            move = chess.Move.from_uci(uci_move)
        except ValueError:
            return MoveResult(
                success=False,
                new_fen=fen,
                is_game_over=False,
                error=f"Invalid UCI format: {uci_move}",
            )

        # Check if move is legal
        if move not in board.legal_moves:
            return MoveResult(
                success=False,
                new_fen=fen,
                is_game_over=False,
                error=f"Illegal move: {uci_move}",
            )

        # Apply the move
        board.push(move)
        new_fen = board.fen()

        # Check game state
        outcome = board.outcome()
        if outcome:
            winner = None
            game_outcome = None

            if outcome.termination == chess.Termination.CHECKMATE:
                game_outcome = "checkmate"
                winner = "white" if outcome.winner else "black"
            elif outcome.termination == chess.Termination.STALEMATE:
                game_outcome = "stalemate"
                winner = "draw"
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                game_outcome = "insufficient_material"
                winner = "draw"
            elif outcome.termination == chess.Termination.SEVENTYFIVE_MOVES:
                game_outcome = "seventy_five_moves"
                winner = "draw"
            elif outcome.termination == chess.Termination.FIVEFOLD_REPETITION:
                game_outcome = "fivefold_repetition"
                winner = "draw"
            elif outcome.termination == chess.Termination.FIFTY_MOVES:
                game_outcome = "fifty_moves"
                winner = "draw"
            elif outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                game_outcome = "threefold_repetition"
                winner = "draw"

            return MoveResult(
                success=True,
                new_fen=new_fen,
                is_game_over=True,
                winner=winner,
                outcome=game_outcome,
            )

        return MoveResult(
            success=True,
            new_fen=new_fen,
            is_game_over=False,
        )

    @staticmethod
    def is_game_over(fen: str) -> bool:
        """Check if the game is over"""
        board = chess.Board(fen)
        return board.is_game_over()

    @staticmethod
    def get_legal_moves(fen: str) -> list[str]:
        """Get all legal moves in UCI format"""
        board = chess.Board(fen)
        return [move.uci() for move in board.legal_moves]

    @staticmethod
    def is_check(fen: str) -> bool:
        """Check if the current player is in check"""
        board = chess.Board(fen)
        return board.is_check()
