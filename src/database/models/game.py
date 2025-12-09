"""Game, Position, and Move database models"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from src.chess.service import ChessService
from src.logger import Logger

from ..database import Base, DatabaseException


class Position(Base):
    """Unique chess positions (FEN states) for deduplication"""

    __tablename__ = "positions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    fen = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    async def get_or_create(
        fen: str, session: AsyncSession, logger: Logger | None = None
    ) -> "Position":
        """Get existing position or create new one"""
        try:
            result = await session.execute(select(Position).filter_by(fen=fen))
            position = result.scalars().first()
            if position:
                return position

            position = Position(fen=fen)
            session.add(position)
            await session.flush()
            return position
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)


class Move(Base):
    """Record of moves in a game"""

    __tablename__ = "moves"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    game_id = Column(String, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(String, ForeignKey("positions.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    uci_move = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    position = relationship("Position")


class Game(Base):
    """Chess game"""

    __tablename__ = "games"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)

    # Players
    white_player_id = Column(String, ForeignKey("users.id"), nullable=True)
    black_player_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Game status
    status = Column(String, default="created", nullable=False)  # created, active, complete
    winner = Column(String, nullable=True)  # white, black, draw
    outcome = Column(String, nullable=True)  # checkmate, stalemate, resignation, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    moves = relationship("Move", backref="game", order_by="Move.move_number")

    @staticmethod
    async def create(
        white_player_id: Optional[str],
        black_player_id: Optional[str],
        session: AsyncSession,
        logger: Logger | None = None,
    ) -> "Game":
        """Create a new game"""
        try:
            game = Game(
                white_player_id=white_player_id,
                black_player_id=black_player_id,
            )
            session.add(game)
            await session.flush()
            return game
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    @staticmethod
    async def get_by_id(
        game_id: str, session: AsyncSession, logger: Logger | None = None
    ) -> Optional["Game"]:
        """Get game by ID"""
        try:
            result = await session.execute(select(Game).filter_by(id=game_id))
            return result.scalars().first()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    @staticmethod
    async def get_user_games(
        user_id: str, session: AsyncSession, logger: Logger | None = None
    ) -> list["Game"]:
        """Get all games for a user"""
        try:
            result = await session.execute(
                select(Game)
                .filter((Game.white_player_id == user_id) | (Game.black_player_id == user_id))
                .order_by(Game.updated_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    async def get_current_fen(self, session: AsyncSession) -> str:
        """Get the current FEN for this game"""
        result = await session.execute(
            select(Position.fen)
            .join(Move, Move.position_id == Position.id)
            .filter(Move.game_id == self.id)
            .order_by(Move.move_number.desc())
            .limit(1)
        )
        row = result.first()
        if row:
            return str(row[0])
        return ChessService.STARTING_FEN

    async def get_move_count(self, session: AsyncSession) -> int:
        """Get number of moves in this game"""
        result = await session.execute(select(func.count(Move.id)).filter(Move.game_id == self.id))
        return result.scalar() or 0

    @staticmethod
    async def record_move(
        game_id: str,
        uci_move: str,
        new_fen: str,
        session: AsyncSession,
        logger: Logger | None = None,
    ) -> None:
        """Record a move in the game"""
        try:
            # Get or create position
            position = await Position.get_or_create(new_fen, session, logger)

            # Get current move count
            result = await session.execute(
                select(func.count(Move.id)).filter(Move.game_id == game_id)
            )
            move_count = result.scalar() or 0

            # Create move record
            move = Move(
                game_id=game_id,
                position_id=position.id,
                move_number=move_count + 1,
                uci_move=uci_move,
            )
            session.add(move)

            # Update game status to active if first move
            if move_count == 0:
                game_result = await session.execute(select(Game).filter_by(id=game_id))
                game = game_result.scalars().first()
                if game and game.status == "created":
                    game.status = "active"  # type: ignore[assignment]

            await session.flush()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    @staticmethod
    async def complete_game(
        game_id: str,
        winner: Optional[str],
        outcome: Optional[str],
        session: AsyncSession,
        logger: Logger | None = None,
    ) -> None:
        """Mark a game as complete"""
        try:
            game_result = await session.execute(select(Game).filter_by(id=game_id))
            game = game_result.scalars().first()
            if game:
                game.status = "complete"  # type: ignore[assignment]
                game.winner = winner  # type: ignore[assignment]
                game.outcome = outcome  # type: ignore[assignment]
            await session.flush()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)
