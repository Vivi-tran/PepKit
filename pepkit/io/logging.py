"""
Light‑weight logging helpers for every script and library in the project.
Usage
-----
from io.logging import setup_logging, get_logger
setup_logging(level="DEBUG", logfile="run.log")
log = get_logger(__name__)
log.info("Hello world!")
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Iterator, Union

DEFAULT_FMT = "%(asctime)s %(levelname)-8s │ %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _coerce_level(level: Union[int, str]) -> int:
    """Accept logging levels as int or case‑insensitive str."""
    if isinstance(level, int):
        return level
    return logging.getLevelName(level.upper())  # type: ignore[arg-type]


def setup_logging(
    level: Union[int, str] = logging.INFO,
    fmt: str = DEFAULT_FMT,
    datefmt: str = DEFAULT_DATEFMT,
    logfile: Optional[Union[str, Path]] = None,
    filesize_limit_mb: int = 5,
    backup_count: int = 2,
    force: bool = False,
) -> None:
    """
    Configure the root logger exactly *once*.
    • All messages ≥ *level* go to stderr (StreamHandler).
    • Optionally duplicate to a rotating file.
    """
    root = logging.getLogger()
    if root.handlers and not force:
        # Already configured—skip so we do not duplicate handlers.
        return

    level_int = _coerce_level(level)
    root.setLevel(level_int)

    # Console handler ---------------------------------------------------------
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(stream_handler)

    # Optional rotating file ---------------------------------------------------
    if logfile:
        logfile = Path(logfile).expanduser().resolve()
        logfile.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            logfile,
            maxBytes=filesize_limit_mb * 1_024 * 1_024,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        root.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Thin wrapper around ``logging.getLogger`` after :func:`setup_logging`."""
    return logging.getLogger(name)


@contextmanager
def temporary_log_level(
    logger: logging.Logger, level: Union[int, str]
) -> Iterator[None]:
    """
    Context‑manager to temporarily change *logger*’s level::

        with temporary_log_level(log, "DEBUG"):
            ...  # more verbose output here
    """
    old = logger.level
    logger.setLevel(_coerce_level(level))
    try:
        yield
    finally:
        logger.setLevel(old)
