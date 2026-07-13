"""Local Obsidian note preview and guarded write helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any, Mapping

from friday.app.obsidian_guard import (
    OBSIDIAN_GUARD_BLOCKED_MESSAGE,
    check_obsidian_note_for_write,
)


OBSIDIAN_WRITE_TOKEN = "OBSIDIAN SCHREIBEN"


@dataclass(frozen=True)
class ObsidianNotePreview:
    """Preview-only markdown note representation."""

    title: str
    safe_filename: str
    relative_path: str
    markdown: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class ObsidianWriteDryRun:
    """Dry-run result for a guarded local Obsidian write."""

    target_path: Path
    would_write: bool
    reason: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def safe_obsidian_filename(value: str) -> str:
    """Return a conservative markdown filename."""
    cleaned = (value or "").strip().lower()
    cleaned = cleaned.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    cleaned = re.sub(r"[^a-z0-9\- ]+", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned).strip("-")
    return f"{cleaned or 'notiz'}.md"


def _frontmatter(kind: str, title: str) -> list[str]:
    return [
        "---",
        f"type: {kind}",
        f"title: {title}",
        "source: friday",
        "external_lookup_used: false",
        "---",
        "",
    ]


def build_contact_note_preview(contact_context: Mapping[str, Any]) -> ObsidianNotePreview:
    """Build a contact note preview without writing to disk."""
    title = str(contact_context.get("display_name") or "Unbekannter Kontakt").strip()
    filename = safe_obsidian_filename(title)
    lines = _frontmatter("contact", title)
    lines.extend(
        [
            f"# {title}",
            "",
            f"- Kontaktart: {contact_context.get('contact_type') or 'unbekannt'}",
            f"- Quelle: {contact_context.get('source_context') or 'lokal'}",
        ]
    )
    nickname = (contact_context.get("nickname") or "").strip()
    if nickname:
        lines.append(f"- Spitzname: {nickname}")
    relationship = (contact_context.get("relationship_context") or "").strip()
    if (
        relationship
        and int(contact_context.get("user_approved_persistence") or 0) == 1
        and int(contact_context.get("sensitivity_checked") or 0) == 1
    ):
        lines.append(f"- Beziehungskontext: {relationship}")

    return ObsidianNotePreview(
        title=title,
        safe_filename=filename,
        relative_path=f"Kontakte/{filename}",
        markdown="\n".join(lines).rstrip() + "\n",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def build_task_note_preview(task: Mapping[str, Any]) -> ObsidianNotePreview:
    """Build a task note preview without writing to disk."""
    title = str(task.get("title") or "Ohne Titel").strip()
    filename = safe_obsidian_filename(title)
    lines = _frontmatter("task", title)
    lines.extend(
        [
            f"# {title}",
            "",
            f"- Status: {task.get('status') or 'open'}",
            f"- Kategorie: {task.get('category') or 'sonstiges'}",
            f"- Faellig: {task.get('due_date') or 'kein Datum'}",
            f"- Prioritaet: {task.get('priority') or 'normal'}",
        ]
    )
    notes = (task.get("notes") or "").strip()
    if notes:
        lines.extend(["", "## Notizen", "", notes])

    return ObsidianNotePreview(
        title=title,
        safe_filename=filename,
        relative_path=f"Aufgaben/{filename}",
        markdown="\n".join(lines).rstrip() + "\n",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def build_project_note_preview(project: Mapping[str, Any]) -> ObsidianNotePreview:
    """Build a generic project note preview without writing to disk."""
    title = str(project.get("title") or project.get("name") or "Projekt").strip()
    filename = safe_obsidian_filename(title)
    lines = _frontmatter("project", title)
    lines.extend([f"# {title}", "", f"- Status: {project.get('status') or 'offen'}"])
    notes = (project.get("notes") or "").strip()
    if notes:
        lines.extend(["", "## Notizen", "", notes])

    return ObsidianNotePreview(
        title=title,
        safe_filename=filename,
        relative_path=f"Projekte/{filename}",
        markdown="\n".join(lines).rstrip() + "\n",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def build_obsidian_target_path(
    vault_path: Path,
    allowed_subdir: str,
    preview: ObsidianNotePreview,
) -> Path:
    """Build and validate the target path inside an allowed vault subdir."""
    root = vault_path.resolve()
    # Treat backslashes as separators on every OS so Windows-style escapes
    # like "..\\outside" are caught on POSIX as well, and reject absolute
    # paths (either OS flavor) before any separator stripping can hide them.
    raw_subdir = (allowed_subdir or "Friday").strip()
    normalized_subdir = raw_subdir.replace("\\", "/")
    if PurePosixPath(normalized_subdir).is_absolute() or PureWindowsPath(raw_subdir).is_absolute():
        raise ValueError("Obsidian-Unterordner muss relativ und innerhalb des Vaults liegen.")
    safe_subdir = normalized_subdir.strip("/") or "Friday"
    subdir_path = Path(safe_subdir)
    if any(part in {"", ".", ".."} for part in subdir_path.parts):
        raise ValueError("Obsidian-Unterordner muss relativ und innerhalb des Vaults liegen.")

    allowed_root = (root / subdir_path).resolve()
    if root != allowed_root and root not in allowed_root.parents:
        raise ValueError("Obsidian-Unterordner liegt außerhalb des Vaults.")

    target = (allowed_root / preview.relative_path).resolve()
    if allowed_root != target and allowed_root not in target.parents:
        raise ValueError("Obsidian-Zielpfad liegt außerhalb des erlaubten Bereichs.")
    return target


def build_obsidian_write_dry_run(
    vault_path: Path,
    allowed_subdir: str,
    preview: ObsidianNotePreview,
    write_enabled: bool = False,
) -> ObsidianWriteDryRun:
    """Return a dry-run description without writing files."""
    target = build_obsidian_target_path(vault_path, allowed_subdir, preview)
    if not write_enabled:
        return ObsidianWriteDryRun(
            target_path=target,
            would_write=False,
            reason="Obsidian Write ist deaktiviert.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )
    if target.exists():
        return ObsidianWriteDryRun(
            target_path=target,
            would_write=False,
            reason="Zieldatei existiert bereits.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )
    return ObsidianWriteDryRun(
        target_path=target,
        would_write=True,
        reason="Würde lokal schreiben.",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def write_obsidian_note_with_approval(
    vault_path: Path,
    allowed_subdir: str,
    preview: ObsidianNotePreview,
    confirmation: str,
    write_enabled: bool = False,
) -> ObsidianWriteDryRun:
    """Write a local note only when enabled and approved with the hard token."""
    target_path = build_obsidian_target_path(vault_path, allowed_subdir, preview)
    if not write_enabled:
        return ObsidianWriteDryRun(
            target_path=target_path,
            would_write=False,
            reason="Obsidian Write ist deaktiviert.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )
    if confirmation != OBSIDIAN_WRITE_TOKEN:
        return ObsidianWriteDryRun(
            target_path=target_path,
            would_write=False,
            reason="Obsidian Write wurde abgebrochen.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    guard_result = check_obsidian_note_for_write(body=preview.markdown)
    if not guard_result.allowed:
        return ObsidianWriteDryRun(
            target_path=target_path,
            would_write=False,
            reason=OBSIDIAN_GUARD_BLOCKED_MESSAGE,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    if target_path.exists():
        return ObsidianWriteDryRun(
            target_path=target_path,
            would_write=False,
            reason="Zieldatei existiert bereits.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(preview.markdown, encoding="utf-8")
    return ObsidianWriteDryRun(
        target_path=target_path,
        would_write=False,
        reason="Obsidian Note wurde lokal geschrieben.",
        preview_only=False,
        persisted=True,
        external_lookup_used=False,
    )
