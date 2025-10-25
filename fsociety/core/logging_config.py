"""
Comprehensive logging configuration for fsociety.

This module provides structured logging with multiple handlers,
log levels, and formatting options.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from rich.logging import RichHandler


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    level: LogLevel = "INFO",
    *,
    log_file: str | Path | None = None,
    log_to_console: bool = True,
    rich_formatting: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure logging for fsociety.

    Args:
        level: Logging level
        log_file: Path to log file (None to disable file logging)
        log_to_console: Whether to log to console
        rich_formatting: Whether to use rich formatting for console
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging("DEBUG", log_file="~/.fsociety/fsociety.log")
        >>> logger.info("Application started")
    """
    # Get or create logger
    logger = logging.getLogger("fsociety")
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        fmt="%(levelname)s: %(message)s"
    )

    # Console handler
    if log_to_console:
        if rich_formatting:
            console_handler = RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                markup=True,
            )
            console_handler.setFormatter(
                logging.Formatter(fmt="%(message)s", datefmt="[%X]")
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(simple_formatter)

        console_handler.setLevel(getattr(logging, level))
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    logger.debug(f"Logging configured with level={level}")
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to "fsociety")

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module loaded")
    """
    if name is None:
        name = "fsociety"
    elif not name.startswith("fsociety"):
        name = f"fsociety.{name}"

    return logging.getLogger(name)
