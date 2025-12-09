import inspect
import logging
import os
from typing import Optional

from fastapi import Request


class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request context"""

    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "method"):
            record.method = record.method
        else:
            record.method = "N/A"
        if hasattr(record, "url"):
            record.url = record.url
        else:
            record.url = "N/A"

        if hasattr(record, "module_name"):
            record.module_name = record.module_name
        else:
            record.module_name = record.module

        return super().format(record)


class Logger:
    """Application logger with request context support"""

    logger: logging.Logger
    handler: logging.Handler
    request: Optional[Request]

    def __init__(
        self, log_path: str | None = None, debug: bool = False, request: Optional[Request] = None
    ) -> None:
        logger = logging.getLogger(__name__)

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger("asyncio").setLevel(logging.WARNING)
            logging.getLogger("aiosqlite").setLevel(logging.WARNING)
        else:
            logging.basicConfig(level=logging.INFO)

        if log_path is not None and log_path.strip() != "":
            log_path = log_path.strip()
            log_dir = os.path.dirname(log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            self.handler = logging.FileHandler(log_path)
        else:
            self.handler = logging.StreamHandler()

        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(self.handler)

        self.logger = logger
        self.request = request

        formatter: logging.Formatter
        if request:
            formatter = RequestFormatter(
                "%(asctime)s - %(module_name)s - %(levelname)s - %(method)s - %(url)s - %(message)s"
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(module_name)s - %(levelname)s - %(message)s"
            )
        self.handler.setFormatter(formatter)

    def with_request(self, request: Request) -> "Logger":
        """Create a new Logger instance with request context"""
        new_logger = Logger.__new__(Logger)
        new_logger.logger = self.logger
        new_logger.handler = self.handler
        new_logger.request = request

        formatter = RequestFormatter(
            "%(asctime)s - %(module_name)s - %(levelname)s - %(method)s - %(url)s - %(message)s"
        )
        new_logger.handler.setFormatter(formatter)
        return new_logger

    def _get_caller_info(self) -> str:
        """Get the module name of the caller"""
        frame = inspect.currentframe()
        if frame is not None:
            caller_frame = frame.f_back
            if caller_frame is not None:
                caller_frame = caller_frame.f_back
                if caller_frame is not None:
                    module = inspect.getmodule(caller_frame)
                    if module is not None:
                        return module.__name__
        return "unknown"

    def _get_extra(self) -> dict:
        """Build extra fields for logging"""
        extra: dict = {"module_name": self._get_caller_info()}
        if self.request:
            extra["method"] = self.request.method
            extra["url"] = str(self.request.url)
        return extra

    def info(self, message: str) -> None:
        self.logger.info(message, extra=self._get_extra())

    def debug(self, message: str) -> None:
        self.logger.debug(message, extra=self._get_extra())

    def warn(self, message: str) -> None:
        self.logger.warning(message, extra=self._get_extra())

    def error(self, message: object) -> None:
        self.logger.error(str(message), extra=self._get_extra())
