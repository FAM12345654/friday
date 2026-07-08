"""Read-only preview model for local backup rotation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackupRotationCandidate:
    """One local backup folder considered for rotation."""

    path: str
    name: str
    selected_for_cleanup: bool
    protected: bool
    reason: str


@dataclass(frozen=True)
class BackupRotationPreview:
    """Side-effect-free preview for local backup rotation."""

    backups_root: str
    keep_latest: int
    candidates: tuple[BackupRotationCandidate, ...]
    cleanup_count: int
    protected_count: int
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _sorted_backup_dirs(backups_root: Path) -> tuple[Path, ...]:
    if not backups_root.exists() or not backups_root.is_dir():
        return ()
    return tuple(
        sorted(
            (path for path in backups_root.iterdir() if path.is_dir()),
            key=lambda path: (path.stat().st_mtime, path.name),
        )
    )


def build_backup_rotation_preview(
    project_root: str | Path,
    keep_latest: int = 1,
) -> BackupRotationPreview:
    """Build a local backup rotation preview without deleting anything."""

    normalized_keep_latest = max(1, int(keep_latest))
    backups_root = Path(project_root) / "local_data" / "backups"
    backup_dirs = _sorted_backup_dirs(backups_root)
    protected_dirs = set(backup_dirs[-normalized_keep_latest:])

    candidates: list[BackupRotationCandidate] = []
    for path in backup_dirs:
        protected = path in protected_dirs
        candidates.append(
            BackupRotationCandidate(
                path=str(path),
                name=path.name,
                selected_for_cleanup=not protected,
                protected=protected,
                reason="latest_backup_protected" if protected else "old_backup_selected",
            )
        )

    return BackupRotationPreview(
        backups_root=str(backups_root),
        keep_latest=normalized_keep_latest,
        candidates=tuple(candidates),
        cleanup_count=sum(1 for candidate in candidates if candidate.selected_for_cleanup),
        protected_count=sum(1 for candidate in candidates if candidate.protected),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
