"""
Path‑manipulation utilities: expansion, normalisation, safety checks.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]


def normalize_path(path: PathLike) -> Path:
    """
    Expand ``~`` and resolve symlinks *without* failing on missing targets.
    """
    p = Path(path).expanduser()
    try:
        return p.resolve(strict=False)
    except (OSError, RuntimeError):
        # On some filesystems resolve() can fail if permissions are restricted
        return p.absolute()


def relative_to(path: PathLike, base: PathLike) -> Path:
    """
    Return a *relative* path (``Path.relative_to`` if possible, else ``os.path.relpath``).
    """
    p = normalize_path(path)
    b = normalize_path(base)
    try:
        return p.relative_to(b)
    except ValueError:
        # Different drive or not a subpath – fall back
        return Path(os.path.relpath(p, b))


def is_subpath(path: PathLike, base: PathLike) -> bool:
    """
    True if *path* is inside *base* (after normalisation).
    """
    try:
        _ = relative_to(path, base)
        return True
    except ValueError:
        return False


def safe_relpath(path: PathLike, base: PathLike) -> str:
    """
    Like :func:`relative_to` but *raises* if ``..`` would be required
    (i.e. path escapes the base directory).
    """
    rel = relative_to(path, base)
    if rel.is_absolute() or rel.parts and rel.parts[0] == "..":
        raise ValueError(f"{path!s} is outside base directory {base!s}")
    return rel.as_posix()


def ensure_dir(path: PathLike, exist_ok: bool = True) -> Path:
    """
    Create the directory (and parents) if it doesn’t exist, returning the ``Path``.
    """
    p = normalize_path(path)
    p.mkdir(parents=True, exist_ok=exist_ok)
    return p


def validate_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Specified path does not exist: {path}")
