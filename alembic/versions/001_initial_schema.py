"""Initial schema with users, games, positions, and moves

Revision ID: 001
Revises:
Create Date: 2024-12-09

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Positions table (unique FEN states)
    op.create_table(
        "positions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("fen", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fen"),
    )

    # Games table
    op.create_table(
        "games",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("white_player_id", sa.String(), nullable=True),
        sa.Column("black_player_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="created"),
        sa.Column("winner", sa.String(), nullable=True),
        sa.Column("outcome", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["white_player_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["black_player_id"], ["users.id"]),
    )

    # Moves table
    op.create_table(
        "moves",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("game_id", sa.String(), nullable=False),
        sa.Column("position_id", sa.String(), nullable=False),
        sa.Column("move_number", sa.Integer(), nullable=False),
        sa.Column("uci_move", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["position_id"], ["positions.id"]),
        sa.UniqueConstraint("game_id", "move_number", name="uq_game_move_number"),
    )

    # Create indexes
    op.create_index("idx_games_updated_at", "games", ["updated_at"])
    op.create_index("idx_moves_game_id", "moves", ["game_id"])


def downgrade() -> None:
    op.drop_index("idx_moves_game_id", table_name="moves")
    op.drop_index("idx_games_updated_at", table_name="games")
    op.drop_table("moves")
    op.drop_table("games")
    op.drop_table("positions")
    op.drop_table("users")
