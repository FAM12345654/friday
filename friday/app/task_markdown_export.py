"""Utilities to convert local Friday tasks into a deterministic markdown format."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


def format_tasks_as_markdown(tasks: Iterable[Mapping[str, Any]]) -> str:
    grouped: dict[str, list[Mapping[str, Any]]] = {
        "open": [],
        "done": [],
        "archived": [],
    }

    for task in tasks:
        status = str(task.get("status") or "open").lower()
        if status not in grouped:
            status = "open"
        grouped[status].append(task)

    lines = ["# Friday Aufgabenexport", ""]

    sections = [
        ("Offene Aufgaben", grouped["open"], "[ ]"),
        ("Erledigte Aufgaben", grouped["done"], "[x]"),
        ("Archivierte Aufgaben", grouped["archived"], "[-]"),
    ]

    for title, section_tasks, marker in sections:
        lines.append(f"## {title}")
        lines.append("")

        if not section_tasks:
            lines.append("_Keine Aufgaben._")
            lines.append("")
            continue

        for task in sorted(section_tasks, key=_sort_key):
            task_title = str(task.get("title") or "Ohne Titel")
            task_id = task.get("id") if task.get("id") is not None else ""
            category = str(task.get("category") or "sonstiges")
            due_date = str(task.get("due_date") or "kein Datum")
            priority = str(task.get("priority") or "normal")
            recurrence = str(task.get("recurrence") or "")
            notes = str(task.get("notes") or "")

            lines.append(f"- {marker} {task_title}")
            lines.append(f"  - ID: {task_id}")
            lines.append(f"  - Kategorie: {category}")
            lines.append(f"  - Fällig: {due_date}")
            lines.append(f"  - Priorität: {priority}")
            if recurrence:
                lines.append(f"  - Wiederholung: {recurrence}")
            if notes:
                lines.append(f"  - Notizen: {notes}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_tasks_markdown(output_path: Path, tasks: Iterable[Mapping[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_tasks_as_markdown(tasks), encoding="utf-8")
    return output_path


def build_default_tasks_export_path(
    base_dir: Path,
    timestamp: datetime | None = None,
) -> Path:
    """Build a controlled local default export path."""
    current = timestamp or datetime.now()
    safe_stamp = current.strftime("%Y%m%d_%H%M%S")
    return base_dir / "local_data" / "exports" / f"friday_tasks_{safe_stamp}.md"


def export_tasks_markdown_to_default_path(
    base_dir: Path,
    tasks: Iterable[Mapping[str, Any]],
    timestamp: datetime | None = None,
) -> Path:
    """Write tasks markdown to the controlled default export path."""
    output_path = build_default_tasks_export_path(base_dir=base_dir, timestamp=timestamp)
    return write_tasks_markdown(output_path=output_path, tasks=tasks)


def _sort_key(task: Mapping[str, Any]) -> int:
    task_id = task.get("id")
    if isinstance(task_id, int):
        return task_id

    try:
        return int(task_id)
    except (TypeError, ValueError):
        return 0
