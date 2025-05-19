import shutil
import fnmatch

from pathlib import Path
from typing import Optional, Iterable, List, Union, Generator, Callable
from contextlib import contextmanager

from pepkit.io.logging import setup_logging

logger = setup_logging()
PathLike = Union[str, Path]
IgnoreFunc = Callable[[str, Iterable[str]], Iterable[str]]


def ensure_dir(path: PathLike, exist_ok: bool = True) -> Path:
    """
    Create directory *path* (including parents) if it doesn’t exist.

    Returns the Path object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=exist_ok)
    logger.debug("Ensured directory exists: %s", p)
    return p


def remove_file(path: PathLike, *, missing_ok: bool = False) -> bool:
    """
    Delete a single file or symlink.

    Returns True if deleted, False if missing_ok=True and file didn’t exist.
    """
    p = Path(path)
    try:
        p.unlink()
        logger.debug("Removed file/link %s", p)
        return True
    except FileNotFoundError:
        if missing_ok:
            logger.debug("File not found (missing_ok=True): %s", p)
            return False
        logger.error("File not found: %s", p)
        raise


def list_files(
    path: PathLike,
    patterns: Optional[Iterable[str]] = None,
    recursive: bool = False,
) -> List[Path]:
    """
    Return a list of files in *path* matching glob *patterns*.

    If recursive=True, searches subdirectories too.
    """
    p = Path(path)
    if not p.is_dir():
        raise NotADirectoryError(f"{p} is not a directory")

    iterator = p.rglob("*") if recursive else p.iterdir()
    out: List[Path] = []
    for entry in iterator:
        if not entry.is_file():
            continue
        if patterns and not any(fnmatch.fnmatch(entry.name, pat) for pat in patterns):
            continue
        out.append(entry)

    logger.debug(
        "Found %d files in %s (patterns=%s, recursive=%s)",
        len(out),
        p,
        patterns,
        recursive,
    )
    return out


def copy_directory(
    src: PathLike,
    dst: PathLike,
    ignore: Optional[IgnoreFunc] = None,
    overwrite: bool = False,
) -> None:
    """
    Copy *src* directory tree to *dst*.

    If overwrite=True, existing dst is removed first.
    """
    src_p = Path(src)
    dst_p = Path(dst)
    if not src_p.is_dir():
        raise NotADirectoryError(f"{src_p} is not a directory")
    if dst_p.exists():
        if not overwrite:
            raise FileExistsError(f"{dst_p} already exists")
        shutil.rmtree(dst_p)
        logger.debug("Overwriting existing directory %s", dst_p)

    shutil.copytree(src_p, dst_p, ignore=ignore)
    logger.debug("Copied directory %s → %s", src_p, dst_p)


# ————————————————————————————————————————————————————————————— #
# Internals for clear_directory                                      #
# ————————————————————————————————————————————————————————————— #


def _validate_directory(path: Path, recreate: bool) -> None:
    if not path.exists():
        if recreate:
            logger.info("Directory %s not found; creating it", path)
            path.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"{path} does not exist")
    elif not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")


def _matches(
    entry: Path, include: Optional[Iterable[str]], exclude: Optional[Iterable[str]]
) -> bool:
    name = entry.name
    if include and not any(fnmatch.fnmatch(name, pat) for pat in include):
        return False
    if exclude and any(fnmatch.fnmatch(name, pat) for pat in exclude):
        return False
    return True


def _remove_entry(entry: Path, ignore_errors: bool) -> bool:
    try:
        if entry.is_symlink() or entry.is_file():
            entry.unlink()
        else:
            shutil.rmtree(entry)
        logger.debug("Removed %s", entry)
        return True
    except Exception as exc:
        if ignore_errors:
            logger.warning("Failed to remove %s: %s", entry, exc)
            return False
        raise


def clear_directory(
    path: PathLike,
    patterns: Optional[Iterable[str]] = None,
    exclude_patterns: Optional[Iterable[str]] = None,
    ignore_errors: bool = False,
    dry_run: bool = False,
    recreate: bool = False,
) -> List[Path]:
    """
    Safely remove contents of a directory.

    Returns a list of Paths that were (or would be, in dry_run) removed.
    """
    dirpath = Path(path)
    _validate_directory(dirpath, recreate)

    removed: List[Path] = []
    for entry in dirpath.iterdir():
        if not _matches(entry, patterns, exclude_patterns):
            continue

        if dry_run:
            logger.info("[DRY RUN] Would remove %s", entry)
            removed.append(entry)
            continue

        if _remove_entry(entry, ignore_errors):
            removed.append(entry)

    if recreate:
        dirpath.mkdir(parents=True, exist_ok=True)
        logger.debug("Re-created directory %s", dirpath)

    return removed


@contextmanager
def temporary_directory(
    path: PathLike,
    patterns: Optional[Iterable[str]] = None,
    ignore_errors: bool = True,
    recreate: bool = True,
) -> Generator[Path, None, None]:
    """
    Context manager that clears a directory on entry and optionally removes it on exit.

    Usage:
        with temporary_directory("/tmp/work") as workdir:
            # workdir is guaranteed clean
            ...
    """
    workdir = Path(path)
    clear_directory(
        workdir, patterns=patterns, ignore_errors=ignore_errors, recreate=True
    )
    try:
        yield workdir
    finally:
        if not recreate:
            clear_directory(workdir, ignore_errors=ignore_errors)
            workdir.rmdir()
            logger.debug("Removed temporary directory %s", workdir)
