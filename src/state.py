from asyncio import Queue
from dataclasses import dataclass, field
from enum import Enum as PyEnum
from typing import Any, Dict, Set

from fastapi import Request

from src.config import Config
from src.database import AsyncDatabase
from src.logger import Logger


class AppStateExceptionType(PyEnum):
    startup_failed = "startup_failed"


class AppStateException(Exception):
    def __init__(self, type: AppStateExceptionType, message: str):
        self.message = message
        self.type = type


@dataclass
class GameChannel:
    """Manages SSE subscribers for a single game"""

    game_id: str
    subscribers: Set["Queue[Any]"] = field(default_factory=set)

    async def broadcast(self, event_data: str, event_type: str = "game-update") -> None:
        """Send event to all subscribers"""
        for queue in list(self.subscribers):
            try:
                await queue.put({"event": event_type, "data": event_data})
            except Exception:
                self.subscribers.discard(queue)

    def subscribe(self) -> "Queue[Any]":
        """Add a new subscriber, return their queue"""
        queue: Queue[Any] = Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: "Queue[Any]") -> None:
        """Remove a subscriber"""
        self.subscribers.discard(queue)


@dataclass
class GameBroadcaster:
    """Manages all game channels for SSE broadcasting"""

    _channels: Dict[str, GameChannel] = field(default_factory=dict)

    async def get_channel(self, game_id: str) -> GameChannel:
        if game_id not in self._channels:
            self._channels[game_id] = GameChannel(game_id)
        return self._channels[game_id]

    async def broadcast_to_game(self, game_id: str, fen: str) -> None:
        """Broadcast FEN to all subscribers - each client renders with own perspective"""
        channel = await self.get_channel(game_id)
        await channel.broadcast(fen, f"fen-update-{game_id}")


@dataclass
class AppState:
    """Application state container"""

    config: Config
    database: AsyncDatabase
    logger: Logger
    game_broadcaster: GameBroadcaster = field(default_factory=GameBroadcaster)

    @classmethod
    def from_config(cls, config: Config) -> "AppState":
        state = cls(
            config=config,
            database=AsyncDatabase(config.postgres_async_url),
            logger=Logger(None, config.debug),
        )
        return state

    async def startup(self) -> None:
        """Run startup logic"""
        try:
            await self.database.initialize()
            self.logger.info("Database initialized")
        except Exception as e:
            raise AppStateException(AppStateExceptionType.startup_failed, str(e)) from e

    async def shutdown(self) -> None:
        """Run shutdown logic"""
        self.logger.info("Shutting down")

    def set_on_request(self, request: Request) -> None:
        """Set request-specific state"""
        request.state.app_state = self
