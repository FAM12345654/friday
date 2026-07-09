"""FastAPI backend for Friday clients."""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from friday.agents import CalendarAgent, ContactContextAgent, MessageAgent, TaskAgent
from friday.app.ai_task_forwarding_draft import build_ai_task_forwarding_draft
from friday.app.local_ollama_activation_gate import build_local_ollama_activation_gate
from friday.app.local_ollama_config_preview import build_local_ollama_config_preview
from friday.config import DEMO_DATE, USE_REAL_TODAY
from friday.storage.database import setup_local_database


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("FRIDAY_CORS_ORIGINS", "").strip()
    if not raw_origins:
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(
    title="Friday API",
    version="1.0.0",
    description="Local REST API for Friday task, message, calendar, contact and privacy views.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    setup_local_database()


task_agent = TaskAgent()
message_agent = MessageAgent(contact_agent=ContactContextAgent())
calendar_agent = CalendarAgent()
contact_agent = ContactContextAgent()


class TaskCreateRequest(BaseModel):
    title: str
    category: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class ContactCreateRequest(BaseModel):
    name: str
    contact_type: Optional[str] = "work"
    notes: Optional[str] = None
    email_address: Optional[str] = None
    whatsapp_target: Optional[str] = None


class TaskForwardDraftRequest(BaseModel):
    task_id: int
    contact_id: int
    channel: str


def _today() -> str:
    if USE_REAL_TODAY:
        return date.today().isoformat()
    return DEMO_DATE


def _envelope(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def _find_message(message_id: int) -> dict[str, Any]:
    for message in message_agent.get_messages():
        if int(message.get("id", 0)) == message_id:
            return message
    raise HTTPException(status_code=404, detail="Message not found.")


def _find_contact(contact_id: int) -> dict[str, Any]:
    for contact in contact_agent.load_contacts():
        if int(contact.get("id", 0)) == contact_id:
            return contact
    raise HTTPException(status_code=404, detail="Contact not found.")


@app.get("/")
def root() -> dict[str, Any]:
    return _envelope({"status": "ok", "service": "friday-api"})


@app.get("/health")
def health() -> dict[str, Any]:
    return _envelope(
        {
            "status": "ok",
            "database": "local",
            "version": app.version,
        },
    )


@app.get("/api/dashboard")
def get_dashboard() -> dict[str, Any]:
    open_tasks = task_agent.get_open_tasks()
    calendar_items = calendar_agent.get_items_for_date(_today())
    messages = message_agent.get_messages()
    contacts = contact_agent.load_contacts()
    return _envelope(
        {
            "date": _today(),
            "summary": {
                "open_tasks": len(open_tasks),
                "messages": len(messages),
                "calendar_items_today": len(calendar_items),
                "contacts": len(contacts),
            },
            "tasks": open_tasks,
            "calendar_items_today": calendar_items,
            "free_slots_today": calendar_agent.get_free_slots_today(),
        },
    )


@app.get("/api/tasks")
def list_tasks(
    date: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    if search:
        tasks = task_agent.search_tasks(query=search, status=status, category=category)
    elif status or category or date:
        tasks = task_agent.filter_tasks(status=status, category=category, due_date=date)
    else:
        tasks = task_agent.get_open_tasks()
    return _envelope(tasks)


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int) -> dict[str, Any]:
    task = task_agent.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _envelope(task)


@app.post("/api/tasks")
def create_task(payload: TaskCreateRequest) -> dict[str, Any]:
    try:
        task = task_agent.create_task(
            title=payload.title,
            category=payload.category,
            due_date=payload.due_date,
            notes=payload.notes,
            priority=payload.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _envelope(task)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdateRequest) -> dict[str, Any]:
    values = payload.dict(exclude_none=True)
    if not values:
        task = task_agent.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return _envelope(task)
    updated = task_agent.edit_task(task_id=task_id, **values)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _envelope(updated)


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int) -> dict[str, Any]:
    deleted = task_agent.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _envelope({"task_id": task_id, "deleted": True})


@app.post("/api/tasks/{task_id}/done")
def complete_task(task_id: int) -> dict[str, Any]:
    updated = task_agent.mark_task_done(task_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _envelope(updated)


@app.post("/api/tasks/{task_id}/archive")
def archive_task(task_id: int) -> dict[str, Any]:
    updated = task_agent.archive_task(task_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _envelope(updated)


@app.get("/api/messages")
def list_messages() -> dict[str, Any]:
    return _envelope(
        {
            "items": message_agent.get_messages(),
            "count": len(message_agent.get_messages()),
        },
    )


@app.get("/api/messages/{message_id}")
def get_message(message_id: int) -> dict[str, Any]:
    return _envelope(_find_message(message_id))


@app.get("/api/messages/{message_id}/reply")
def reply_hint(message_id: int) -> dict[str, Any]:
    message = _find_message(message_id)
    return _envelope(
        {
            "message_id": message_id,
            "draft_text": message_agent.create_reply_suggestion(message),
            "contact_type": message_agent.get_contact_type(message.get("sender", "")),
            "intent": message_agent.detect_intent(message.get("text", "")),
        },
    )


@app.post("/api/messages/{message_id}/reply")
def send_message_reply(message_id: int) -> dict[str, Any]:
    return _envelope(
        {
            "status": "queued",
            "message_id": message_id,
            "note": "Friday arbeitet im lokalen Read-Only-Modus; es wird noch nicht gesendet.",
        },
    )


@app.post("/api/messages/{message_id}/task-suggestions")
def create_task_suggestions_for_message(message_id: int) -> dict[str, Any]:
    _find_message(message_id)
    suggestions = message_agent.generate_local_task_suggestions()
    return _envelope(
        {
            "message_id": message_id,
            "created": suggestions,
            "count": len(suggestions),
        },
    )


@app.get("/api/messages/suggestions")
def list_suggestions() -> dict[str, Any]:
    return _envelope(
        {
            "message_suggestions": message_agent.get_pending_suggestions(),
            "task_suggestions": message_agent.get_pending_task_suggestions(),
        },
    )


@app.post("/api/messages/suggestions/{suggestion_id}/approve")
def approve_message_suggestion(suggestion_id: int) -> dict[str, Any]:
    suggestion = message_agent.approve_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Message suggestion not found.")
    return _envelope(suggestion)


@app.post("/api/messages/suggestions/{suggestion_id}/reject")
def reject_message_suggestion(suggestion_id: int) -> dict[str, Any]:
    suggestion = message_agent.reject_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Message suggestion not found.")
    return _envelope(suggestion)


@app.post("/api/messages/task-suggestions/{suggestion_id}/approve")
def approve_task_suggestion(suggestion_id: int) -> dict[str, Any]:
    suggestion = message_agent.approve_task_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Task suggestion not found.")
    return _envelope(suggestion)


@app.post("/api/messages/task-suggestions/{suggestion_id}/reject")
def reject_task_suggestion(suggestion_id: int) -> dict[str, Any]:
    suggestion = message_agent.reject_task_suggestion(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Task suggestion not found.")
    return _envelope(suggestion)


@app.get("/api/calendar")
def get_calendar(date: Optional[str] = Query(default=None)) -> dict[str, Any]:
    date_value = date or _today()
    return _envelope(
        {
            "date": date_value,
            "items": calendar_agent.get_items_for_date(date_value),
            "free_slots": calendar_agent.get_free_slots_for_date(date_value),
        },
    )


@app.get("/api/calendar/{message_id}/slots")
def generate_slots(message_id: int, duration_minutes: int = Query(default=60)) -> dict[str, Any]:
    _find_message(message_id)
    return _envelope(
        {
            "message_id": message_id,
            "date": _today(),
            "slots": calendar_agent.generate_calendar_suggestions_for_message(
                message_id=message_id,
                date_iso=_today(),
                duration_minutes=duration_minutes,
            ),
        },
    )


@app.get("/api/contacts")
def list_contacts() -> dict[str, Any]:
    return _envelope(contact_agent.load_contacts())


@app.post("/api/contacts")
def create_contact(payload: ContactCreateRequest) -> dict[str, Any]:
    try:
        contact = contact_agent.create_contact(
            name=payload.name,
            contact_type=payload.contact_type,
            notes=payload.notes,
            email_address=payload.email_address,
            whatsapp_target=payload.whatsapp_target,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _envelope(contact)


@app.post("/api/ai/task-forward-draft")
def create_ai_task_forward_draft(payload: TaskForwardDraftRequest) -> dict[str, Any]:
    task = task_agent.get_task_by_id(payload.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    contact = _find_contact(payload.contact_id)
    draft = build_ai_task_forwarding_draft(
        task=task,
        contact=contact,
        channel=payload.channel,
    )
    return _envelope(asdict(draft))


@app.get("/api/ai/status")
def get_ai_status(run_health_check: bool = Query(default=False)) -> dict[str, Any]:
    gate = build_local_ollama_activation_gate(run_health_check=run_health_check)
    return _envelope(asdict(gate))


@app.get("/api/ai/ollama/config-preview")
def get_ollama_config_preview(
    model: str = Query(default=""),
    base_url: str = Query(default="http://localhost:11434"),
    enable_requested: bool = Query(default=True),
) -> dict[str, Any]:
    preview = build_local_ollama_config_preview(
        model=model,
        base_url=base_url,
        enable_requested=enable_requested,
    )
    return _envelope(asdict(preview))


@app.get("/api/privacy")
def get_privacy() -> dict[str, Any]:
    return _envelope(
        {
            "mode": "local",
            "external_services": {
                "email": False,
                "whatsapp": False,
                "sms": False,
                "calendar": False,
                "weather": False,
                "music": False,
            },
            "writes": {
                "exports": False,
                "messages_send": False,
                "contacts_write": True,
            },
            "notes": "Kontakte koennen lokal gespeichert werden; externe Nachrichten bleiben deaktiviert.",
        },
    )
