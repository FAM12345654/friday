"""Local Obsidian Brain preview helpers.

This module intentionally stays local and side-effect free. It builds note
previews from existing local records, but it does not read from or write to an
Obsidian vault.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from friday import config
from friday.app.obsidian_note_preview import (
    OBSIDIAN_WRITE_TOKEN,
    ObsidianNotePreview,
    build_contact_note_preview,
    build_project_note_preview,
    build_task_note_preview,
)


@dataclass(frozen=True)
class ObsidianBrainPreview:
    """A grouped preview of notes Friday could create for Obsidian."""

    task_previews: tuple[ObsidianNotePreview, ...]
    contact_previews: tuple[ObsidianNotePreview, ...]
    project_previews: tuple[ObsidianNotePreview, ...]
    preview_only: bool = True
    persisted: bool = False
    external_lookup_used: bool = False

    def all_previews(self) -> tuple[ObsidianNotePreview, ...]:
        """Return all note previews in display/write order."""
        return self.task_previews + self.contact_previews + self.project_previews


@dataclass(frozen=True)
class ObsidianBrainFinalizationGate:
    """Read-only release gate summary for the local Obsidian Brain block."""

    status: str
    vault_path_configured: bool
    write_enabled: bool
    allowed_subdir: str
    approval_token_required: str
    completed_checks: tuple[str, ...]
    required_write_gates: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    deferred_items: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False
    external_lookup_used: bool = False


def build_obsidian_brain_preview(
    tasks: Iterable[Mapping[str, object]] = (),
    contacts: Iterable[Mapping[str, object]] = (),
    projects: Iterable[Mapping[str, object]] = (),
) -> ObsidianBrainPreview:
    """Build a local-only Obsidian Brain preview from existing records."""

    return ObsidianBrainPreview(
        task_previews=tuple(build_task_note_preview(task) for task in tasks),
        contact_previews=tuple(
            build_contact_note_preview(contact) for contact in contacts
        ),
        project_previews=tuple(
            build_project_note_preview(project) for project in projects
        ),
    )


def build_obsidian_brain_finalization_gate() -> ObsidianBrainFinalizationGate:
    """Return the local-only Obsidian Brain release gate status."""

    write_enabled = bool(config.OBSIDIAN_WRITE_ENABLED)
    status = (
        "guarded_write_possible"
        if write_enabled
        else "finalized_preview_ready_write_disabled"
    )

    return ObsidianBrainFinalizationGate(
        status=status,
        vault_path_configured=bool(config.OBSIDIAN_VAULT_PATH.strip()),
        write_enabled=write_enabled,
        allowed_subdir=config.OBSIDIAN_ALLOWED_SUBDIR,
        approval_token_required=OBSIDIAN_WRITE_TOKEN,
        completed_checks=(
            "vault_config_defaults_safe",
            "contact_task_project_previews_available",
            "write_dry_run_available",
            "sensitive_content_guard_before_write",
            "hard_token_required_for_write",
            "local_only_no_external_lookup",
        ),
        required_write_gates=(
            "OBSIDIAN_VAULT_PATH must be configured explicitly",
            "OBSIDIAN_WRITE_ENABLED must be True",
            "confirmation must exactly match OBSIDIAN SCHREIBEN",
            "target path must stay inside OBSIDIAN_ALLOWED_SUBDIR",
            "sensitive-content guard must allow the rendered note",
            "target file must not already exist",
        ),
        blocked_actions=(
            "automatic_vault_detection",
            "automatic_obsidian_write",
            "cloud_sync_or_provider_call",
            "write_sensitive_free_text",
            "overwrite_existing_note",
        ),
        deferred_items=(
            "cli_write_wizard",
            "vault_sync_history",
            "user_selected_batch_write",
        ),
    )
