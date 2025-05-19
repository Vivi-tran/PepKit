import os
import sys
import logging
from rdkit import RDLogger
from contextlib import contextmanager
from typing import Union, Optional


def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_to_file: bool = False,
    filename: Optional[str] = None,
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    logger_name: Optional[str] = None,
    file_mode: str = "a",
) -> logging.Logger:
    """
    Configure and return a logger with console and optional file handlers.

    Parameters:
        level: Logging level (int or str), e.g. logging.DEBUG or "DEBUG".
        log_to_file: Whether to also log to a file.
        filename: Path to the log file (required if log_to_file=True).
        fmt: Log message format string.
        datefmt: Date format string for timestamps.
        logger_name: Name of the logger to configure; configures root logger if None.
        file_mode: Mode for the file handler: 'a' to append, 'w' to overwrite.

    Returns:
        Configured logging.Logger instance.
    """
    # Convert string level to numeric
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())

    # Get or create specified logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Formatter for all handlers
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Remove existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (optional)
    if log_to_file:
        if not filename:
            raise ValueError("`filename` must be provided when `log_to_file=True`")
        # Create file handler with specified mode ('a' to append, 'w' to overwrite)
        fh = logging.FileHandler(filename, mode=file_mode)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def disable_rdkit_warnings(
    suppress_cpp: bool = True, level: int = RDLogger.CRITICAL
) -> None:
    """
    Silences RDKit Python logging and optional C++ warnings.

    Parameters:
    - suppress_cpp (bool): If True, redirects C/C++ stderr output to os.devnull,
      suppressing any low-level RDKit messages.
    - level (int): RDKit logging level to set (e.g., RDLogger.CRITICAL to suppress all).

    Usage:
        disable_rdkit_warnings()
        # import and use RDKit without warnings
    """
    # Disable RDKit Python logs (from rdApp.*)
    RDLogger.DisableLog("rdApp.*")
    rd_logger = RDLogger.logger()
    rd_logger.setLevel(level)

    if suppress_cpp:
        # Redirect C++ stderr messages (e.g., from RDKit's C++ core) to null
        sys.stderr = open(os.devnull, "w")


@contextmanager
def rdkit_warning_suppression(suppress_cpp: bool = True):
    """
    Context manager to temporarily silence RDKit warnings (Python and C++).

    Example:
        with rdkit_warning_suppression():
            mol = Chem.MolFromSmiles('invalid')  # no warnings shown
    """
    # Save original stderr
    orig_err = sys.stderr
    try:
        disable_rdkit_warnings(suppress_cpp=suppress_cpp)
        yield
    finally:
        # Restore stderr
        if suppress_cpp:
            sys.stderr.close()
        sys.stderr = orig_err
