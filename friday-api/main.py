"""FastAPI backend for Friday clients."""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from friday import config
from friday.agents import (
    CalendarAgent,
    ContactContextAgent,
    MessageAgent,
    TaskAgent,
    build_email_forward_preview,
    build_whatsapp_forward_preview,
)
from friday.app.ai_task_forwarding_draft import build_ai_task_forwarding_draft
from friday.app.calendar_event_extraction import extract_calendar_event_candidate
from friday.app.contact_category_classifier import classify_contact_category
from friday.app.email_account_store import (
    EMAIL_ACCOUNT_DELETE_TOKEN,
    EMAIL_ACCOUNT_SAVE_TOKEN,
    build_email_account_from_plain_password,
    build_email_account_from_preset,
    decrypt_email_account_password,
    delete_email_account,
    email_account_status,
    load_email_account,
    save_email_account,
)
from friday.app.email_activation_gate import EMAIL_ACTIVATION_TOKEN, build_email_activation_gate
from friday.app.email_imap_reader import check_imap_login, read_recent_inbox_emails
from friday.app.email_send_guard import EMAIL_SEND_TOKEN, check_email_send_allowed, log_email_send
from friday.app.email_smtp_sender import check_smtp_login, send_single_email
from friday.app.local_ollama_activation_gate import build_local_ollama_activation_gate
from friday.app.local_ollama_config_apply_guard import build_local_ollama_config_apply_gate
from friday.app.local_ollama_config_preview import build_local_ollama_config_preview
from friday.app.local_model_provider import get_local_model_fallback_count
from friday.app.messaging_audit_preview import build_messaging_audit_preview
from friday.app.setup_status import build_setup_status
from friday.app.whatsapp_bridge_activation_gate import (
    WHATSAPP_BRIDGE_ACTIVATION_TOKEN,
    build_whatsapp_bridge_activation_gate,
)
from friday.app.whatsapp_inbox_store import (
    bridge_token_matches,
    get_whatsapp_bridge_status,
    insert_whatsapp_message,
    read_recent_whatsapp_messages,
)
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


class ContactCategoryPreviewRequest(BaseModel):
    display_name: str
    context_text: str | None = None
    model_raw_category: str | None = None


class TaskForwardDraftRequest(BaseModel):
    task_id: int
    contact_id: int
    channel: str


class OllamaConfigApplyGateRequest(BaseModel):
    model: str
    base_url: str | None = "http://localhost:11434"
    approval_token: str
    scanner_smoke_passed: bool = False
    health_check_passed: bool = False


class EmailAccountConnectRequest(BaseModel):
    preset_name: str = "gmail"
    display_name: str | None = None
    email_address: str
    username: str
    app_password: str
    approval_token: str
    smtp_host: str | None = None
    smtp_port: int | None = None
    imap_host: str | None = None
    imap_port: int | None = None


class EmailAccountDeleteRequest(BaseModel):
    approval_token: str


class EmailActivationGateRequest(BaseModel):
    approval_token: str
    scanner_smoke_passed: bool = False


class EmailSendRequest(BaseModel):
    task_id: int
    contact_id: int
    subject: str | None = None
    body: str
    approval_token: str


class WhatsAppIngestRequest(BaseModel):
    chat_id: str
    sender_name: str | None = None
    sender_number: str | None = None
    body: str
    received_at: str | None = None


class WhatsAppBridgeActivationGateRequest(BaseModel):
    approval_token: str
    scanner_smoke_passed: bool = False


class CalendarEventExtractRequest(BaseModel):
    text: str
    base_date: str | None = None
    duration_minutes: int = 60


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


@app.get("/api/setup/status")
def get_setup_status() -> dict[str, Any]:
    return _envelope(build_setup_status())


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


@app.post("/api/messages/{message_id}/calendar-event-suggestions")
def create_calendar_event_suggestion_for_message(message_id: int) -> dict[str, Any]:
    message = _find_message(message_id)
    extraction = extract_calendar_event_candidate(str(message.get("text") or ""))
    suggestion = message_agent.create_calendar_event_suggestion(message)
    return _envelope(
        {
            "message_id": message_id,
            "created": suggestion is not None,
            "suggestion": suggestion,
            "extraction": extraction.to_dict(),
            "calendar_write_enabled": False,
        }
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


@app.post("/api/calendar/extract-event")
def extract_calendar_event(payload: CalendarEventExtractRequest) -> dict[str, Any]:
    extraction = extract_calendar_event_candidate(
        payload.text,
        base_date=payload.base_date,
        duration_minutes=payload.duration_minutes,
    )
    return _envelope(
        {
            "extraction": extraction.to_dict(),
            "calendar_write_enabled": False,
            "review_required": True,
        }
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


@app.post("/api/contacts/category-preview")
def preview_contact_category(payload: ContactCategoryPreviewRequest) -> dict[str, Any]:
    preview = classify_contact_category(
        display_name=payload.display_name,
        context_text=payload.context_text,
        model_raw_category=payload.model_raw_category,
    )
    return _envelope(preview.to_dict())


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
    if draft.channel == "whatsapp":
        channel_preview = build_whatsapp_forward_preview(
            draft_text=draft.draft_text,
            whatsapp_target=contact.get("whatsapp_target"),
        )
    else:
        channel_preview = build_email_forward_preview(
            draft_text=draft.draft_text,
            email_address=contact.get("email_address"),
            subject=f"Aufgabe: {draft.task_title}",
        )

    audit_preview = build_messaging_audit_preview(
        task_id=draft.task_id,
        task_title=draft.task_title,
        contact_id=int(draft.contact_id) if str(draft.contact_id or "").isdigit() else None,
        contact_name=draft.contact_name,
        channel=draft.channel,  # type: ignore[arg-type]
        target=draft.target,
        draft_text=draft.draft_text,
        approval_token=draft.approval_token_required,
        mode="mock",
        status="link_built" if channel_preview.deep_link else "draft_created",
        provider=draft.provider,
    )

    response = asdict(draft)
    response.update(
        {
            "deep_link": channel_preview.deep_link,
            "deep_link_message": channel_preview.message,
            "sent": False,
            "channel_preview": asdict(channel_preview),
            "audit_preview": asdict(audit_preview),
        }
    )
    return _envelope(response)


@app.get("/api/accounts/email/status")
def get_email_account_status() -> dict[str, Any]:
    return _envelope(email_account_status())


@app.post("/api/accounts/email/connect")
def connect_email_account(payload: EmailAccountConnectRequest) -> dict[str, Any]:
    try:
        if payload.smtp_host and payload.smtp_port and payload.imap_host and payload.imap_port:
            account = build_email_account_from_plain_password(
                display_name=payload.display_name or payload.email_address,
                email_address=payload.email_address,
                smtp_host=payload.smtp_host,
                smtp_port=payload.smtp_port,
                imap_host=payload.imap_host,
                imap_port=payload.imap_port,
                username=payload.username,
                app_password=payload.app_password,
                last_test_ok=False,
            )
        else:
            account = build_email_account_from_preset(
                preset_name=payload.preset_name,
                email_address=payload.email_address,
                username=payload.username,
                app_password=payload.app_password,
                last_test_ok=False,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    smtp_test = check_smtp_login(account=account, app_password=payload.app_password)
    imap_test = check_imap_login(account=account, app_password=payload.app_password)
    if not smtp_test.ok or not imap_test.ok:
        return _envelope(
            {
                "connected": False,
                "saved": False,
                "smtp_ok": smtp_test.ok,
                "imap_ok": imap_test.ok,
                "message": "Verbindungstest fehlgeschlagen. Konto wurde nicht gespeichert.",
            }
        )

    tested_account = build_email_account_from_plain_password(
        display_name=account.display_name,
        email_address=account.email_address,
        smtp_host=account.smtp_host,
        smtp_port=account.smtp_port,
        imap_host=account.imap_host,
        imap_port=account.imap_port,
        username=account.username,
        app_password=payload.app_password,
        last_test_ok=True,
    )
    result = save_email_account(
        tested_account,
        approval_token=payload.approval_token,
    )
    if not result.persisted:
        raise HTTPException(status_code=403, detail=result.message)
    return _envelope(
        {
            "connected": True,
            "saved": True,
            "smtp_ok": True,
            "imap_ok": True,
            "status": email_account_status(),
        }
    )


@app.post("/api/accounts/email/test")
def test_email_account_connection() -> dict[str, Any]:
    account = load_email_account()
    if account is None:
        return _envelope({"connected": False, "smtp_ok": False, "imap_ok": False})
    app_password = decrypt_email_account_password(account)
    smtp_test = check_smtp_login(account=account, app_password=app_password)
    imap_test = check_imap_login(account=account, app_password=app_password)
    return _envelope(
        {
            "connected": True,
            "smtp_ok": smtp_test.ok,
            "imap_ok": imap_test.ok,
            "last_test_ok": smtp_test.ok and imap_test.ok,
        }
    )


@app.delete("/api/accounts/email")
def delete_email_account_endpoint(payload: EmailAccountDeleteRequest) -> dict[str, Any]:
    result = delete_email_account(approval_token=payload.approval_token)
    if not result.allowed:
        raise HTTPException(status_code=403, detail=result.message)
    return _envelope({"deleted": True, "status": email_account_status()})


@app.post("/api/accounts/email/activation-gate")
def get_email_activation_gate(payload: EmailActivationGateRequest) -> dict[str, Any]:
    gate = build_email_activation_gate(
        approval_token=payload.approval_token,
        scanner_smoke_passed=payload.scanner_smoke_passed,
    )
    return _envelope(asdict(gate))


@app.get("/api/messages/email-inbox")
def get_email_inbox_preview(limit: int = Query(default=10)) -> dict[str, Any]:
    account = load_email_account()
    if account is None:
        return _envelope({"connected": False, "items": [], "message": "Kein E-Mail-Konto verbunden."})
    app_password = decrypt_email_account_password(account)
    result = read_recent_inbox_emails(account=account, app_password=app_password, limit=limit)
    return _envelope(
        {
            "connected": True,
            "ok": result.ok,
            "items": [asdict(item) for item in result.items],
            "error": result.error,
            "read_only": result.read_only,
        }
    )


@app.get("/api/whatsapp/status")
def get_whatsapp_status() -> dict[str, Any]:
    return _envelope(get_whatsapp_bridge_status(message_agent.db_path))


@app.get("/api/whatsapp/messages")
def get_whatsapp_messages(limit: int = Query(default=10)) -> dict[str, Any]:
    items = read_recent_whatsapp_messages(limit=limit, db_path=message_agent.db_path)
    return _envelope(
        {
            "items": items,
            "count": len(items),
            "status": get_whatsapp_bridge_status(message_agent.db_path),
            "read_only": True,
        }
    )


@app.post("/api/whatsapp/ingest")
def ingest_whatsapp_message(
    payload: WhatsAppIngestRequest,
    x_friday_whatsapp_bridge_token: str | None = Header(default=None),
) -> dict[str, Any]:
    if not config.ENABLE_WHATSAPP_BRIDGE_READ:
        raise HTTPException(
            status_code=403,
            detail="WhatsApp Read-Bridge ist deaktiviert.",
        )
    if not bridge_token_matches(x_friday_whatsapp_bridge_token):
        raise HTTPException(
            status_code=403,
            detail="WhatsApp Bridge Token wurde abgelehnt.",
        )

    result = insert_whatsapp_message(
        chat_id=payload.chat_id,
        sender_name=payload.sender_name,
        sender_number=payload.sender_number,
        body=payload.body,
        received_at=payload.received_at,
        db_path=message_agent.db_path,
    )
    process_result = message_agent.process_unprocessed_whatsapp_messages()
    return _envelope(
        {
            "stored": result.stored,
            "duplicate": result.duplicate,
            "message_id": result.message_id,
            "processed_count": process_result.processed_count,
            "message_suggestions_created": process_result.message_suggestions_created,
            "task_suggestions_created": process_result.task_suggestions_created,
            "send_via_bridge": False,
        }
    )


@app.post("/api/whatsapp/activation-gate")
def get_whatsapp_bridge_activation_gate(
    payload: WhatsAppBridgeActivationGateRequest,
) -> dict[str, Any]:
    gate = build_whatsapp_bridge_activation_gate(
        approval_token=payload.approval_token,
        scanner_smoke_passed=payload.scanner_smoke_passed,
    )
    return _envelope(asdict(gate))


@app.post("/api/accounts/email/send-task-forward")
def send_task_forward_email(payload: EmailSendRequest) -> dict[str, Any]:
    task = task_agent.get_task_by_id(payload.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    contact = _find_contact(payload.contact_id)
    recipient = str(contact.get("email_address") or "")
    subject = payload.subject or f"Aufgabe: {task.get('title', '')}"
    account = load_email_account()
    guard = check_email_send_allowed(
        recipient=recipient,
        subject=subject,
        approval_token=payload.approval_token,
        account=account,
    )
    if not guard.allowed:
        return _envelope(
            {
                "sent": False,
                "guard": asdict(guard),
                "message": "E-Mail wurde nicht gesendet.",
            }
        )
    assert account is not None
    app_password = decrypt_email_account_password(account)
    send_result = send_single_email(
        account=account,
        app_password=app_password,
        recipient=recipient,
        subject=subject,
        body=payload.body,
    )
    log_email_send(
        recipient=recipient,
        subject=subject,
        message_id=send_result.message_id,
        status="sent" if send_result.sent else "failed",
    )
    audit = build_messaging_audit_preview(
        task_id=payload.task_id,
        task_title=str(task.get("title") or ""),
        contact_id=payload.contact_id,
        contact_name=str(contact.get("name") or ""),
        channel="email",
        target=recipient,
        draft_text=payload.body,
        approval_token=EMAIL_SEND_TOKEN,
        mode="live",
        status="sent" if send_result.sent else "failed",
        provider="smtp",
        external_message_id=send_result.message_id,
    )
    return _envelope(
        {
            "sent": send_result.sent,
            "message_id": send_result.message_id,
            "error": send_result.error,
            "audit": asdict(audit),
            "guard": asdict(guard),
        }
    )


@app.get("/api/ai/status")
def get_ai_status(run_health_check: bool = Query(default=False)) -> dict[str, Any]:
    gate = build_local_ollama_activation_gate(run_health_check=run_health_check)
    payload = asdict(gate)
    payload.update(
        {
            "configured_model": config.OLLAMA_MODEL,
            "configured_base_url": config.OLLAMA_BASE_URL,
            "fallback_count": get_local_model_fallback_count(),
            "local_ollama_enabled": config.ENABLE_LOCAL_OLLAMA,
        }
    )
    return _envelope(payload)


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


@app.post("/api/ai/ollama/config-apply-gate")
def get_ollama_config_apply_gate(payload: OllamaConfigApplyGateRequest) -> dict[str, Any]:
    preview = build_local_ollama_config_preview(
        model=payload.model,
        base_url=payload.base_url,
        enable_requested=True,
    )
    gate = build_local_ollama_config_apply_gate(
        preview=preview,
        approval_token=payload.approval_token,
        scanner_smoke_passed=payload.scanner_smoke_passed,
        health_check_passed=payload.health_check_passed,
    )
    return _envelope(asdict(gate))


@app.get("/api/privacy")
def get_privacy() -> dict[str, Any]:
    return _envelope(
        {
            "mode": "local",
            "external_services": {
                "email": False,
                "whatsapp": False,
                "whatsapp_bridge_read": config.ENABLE_WHATSAPP_BRIDGE_READ,
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
