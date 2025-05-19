"""
High‑level file I/O helpers for JSON, CSV, text, and atomic writes.
"""

from __future__ import annotations
import json
import csv
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Union, Optional

import pandas as pd

PathLike = Union[str, Path]


# --------------------------------------------------------------------------- #
# JSON                                                                       #
# --------------------------------------------------------------------------- #
def read_json(path: PathLike, encoding: str = "utf-8") -> Any:
    with open(path, "r", encoding=encoding) as f:
        return json.load(f)


def write_json(
    path: PathLike, obj: Any, encoding: str = "utf-8", indent: int = 2
) -> None:
    atomic_write(
        path,
        json.dumps(obj, indent=indent, ensure_ascii=False) + "\n",
        mode="w",
        encoding=encoding,
    )


# --------------------------------------------------------------------------- #
# CSV                                                                         #
# --------------------------------------------------------------------------- #
def read_csv(path: PathLike, **kwargs) -> pd.DataFrame:
    """
    Thin wrapper around :func:`pandas.read_csv` that expands ``~`` automatically.
    """
    return pd.read_csv(Path(path).expanduser(), **kwargs)


def write_csv(
    path: PathLike,
    df: pd.DataFrame,
    index: bool = False,
    encoding: str = "utf-8",
    **kwargs,
) -> None:
    atomic_write(
        path,
        df.to_csv(index=index, encoding=encoding, **kwargs),
        mode="w",
        encoding=encoding,
    )


# --------------------------------------------------------------------------- #
# Plain text                                                                  #
# --------------------------------------------------------------------------- #
def read_text(path: PathLike, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_text(path: PathLike, text: str, encoding: str = "utf-8") -> None:
    atomic_write(path, text, mode="w", encoding=encoding)


# --------------------------------------------------------------------------- #
# Atomic write                                                                #
# --------------------------------------------------------------------------- #
def atomic_write(
    path: PathLike,
    data: str,
    mode: str = "w",
    encoding: Optional[str] = "utf-8",
    newline: Optional[str] = None,
) -> None:
    """
    Write *data* to *path* via a temporary file and `shutil.move` to guarantee
    that either the previous version or the new version exists (never a half‑write).
    """
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode=mode, delete=False, dir=target.parent, encoding=encoding, newline=newline
    ) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    # Move into place (overwrites atomically on POSIX)
    shutil.move(tmp_path, target)


# --------------------------------------------------------------------------- #
# Delimited text helpers                                                      #
# --------------------------------------------------------------------------- #
def write_tsv(
    path: PathLike,
    rows: Iterable[Dict[str, Any]],
    fieldnames: Iterable[str],
    encoding: str = "utf-8",
) -> None:
    """
    Quick TSV writer for small data structures.
    """
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
