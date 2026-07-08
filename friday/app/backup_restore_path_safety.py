"""Shared forbidden-path checks for local Backup/Restore flows."""

from __future__ import annotations

from pathlib import Path


FORBIDDEN_BACKUP_PATH_LABELS: tuple[str, ...] = (
    "secret",
    "secrets",
    "token",
    "tokens",
    "apikey",
    "apikeys",
    "credential",
    "credentials",
    "password",
    "passwords",
    "privatekey",
    "privatekeys",
    "obsidianvault",
)


def _compact_label(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def _is_forbidden_path_part(part: str) -> bool:
    lowered = part.strip().lower()
    if lowered == ".env" or lowered.startswith(".env."):
        return True
    if lowered == ".obsidian":
        return True

    compact = _compact_label(lowered)
    stem_compact = _compact_label(Path(part).stem)
    return compact in FORBIDDEN_BACKUP_PATH_LABELS or stem_compact in FORBIDDEN_BACKUP_PATH_LABELS


def _is_symlink_or_junction(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        is_junction = getattr(path, "is_junction", None)
        return bool(is_junction is not None and is_junction())
    except OSError:
        return True


def _path_chain(path: Path, root: Path) -> tuple[Path, ...]:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return (path,)

    current = root
    chain = [current]
    for part in relative.parts:
        current = current / part
        chain.append(current)
    return tuple(chain)


def _resolved_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def is_forbidden_backup_restore_path(path: Path, root: Path | None = None) -> bool:
    """Return whether a backup/restore candidate path must be excluded or blocked."""

    candidate_path = Path(path)

    if _is_symlink_or_junction(candidate_path):
        return True

    candidate = candidate_path
    if root is not None:
        root_path = Path(root)
        if not _resolved_inside(candidate_path, root_path):
            return True
        if any(_is_symlink_or_junction(part) for part in _path_chain(candidate_path, root_path)):
            return True
        try:
            candidate = candidate_path.relative_to(root_path)
        except ValueError:
            return True

    return any(_is_forbidden_path_part(part) for part in candidate.parts)
