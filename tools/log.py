"""
Logger module for application logging with file rotation and colored console output.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional

import colorlog

from _setting import SYSTEM

# Logging configuration constants
LOGGING_LEVEL = logging.INFO
CONSOLE_FORMAT = (
    "%(log_color)s[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s"
)
FILE_FORMAT = "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s"
LOGGING_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_PATH = os.path.join(os.getcwd(), "loginfo.log")

# File rotation configuration
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 3


def _create_logger(level: int = LOGGING_LEVEL) -> logging.Logger:
    """
    Create and configure a logger with console and file handlers.

    Args:
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(level)

    # Standard console handler (also with color for consistency)
    stdout_handler = colorlog.StreamHandler(sys.stdout)
    stdout_formatter = colorlog.ColoredFormatter(CONSOLE_FORMAT)
    stdout_handler.setFormatter(stdout_formatter)

    # Rotating file handler (without color formatting)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(FILE_FORMAT, datefmt=LOGGING_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger


def initialize_logger(level: Optional[int] = None) -> None:
    """
    Initialize or reinitialize the global logger instance.

    Args:
        level: Logging level. If None, uses debug level from SYSTEM config or default level
    """
    global logger_instance

    if level is None:
        level = logging.DEBUG if SYSTEM.get("debug") else LOGGING_LEVEL

    logger_instance = _create_logger(level)


# Initialize logger instance
logger_instance = _create_logger(
    logging.DEBUG if SYSTEM.get("debug") else LOGGING_LEVEL
)
