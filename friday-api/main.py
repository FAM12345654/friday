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
from friday.app.account_policy_engine import build_ai_context, resolve_write_target
from friday.app.account_policy_store import (
    POLICY_SAVE_TOKEN,
    create_account_policy,
    delete_account_policy,
    list_account_policies,
    update_account_policy,
)
from friday.app.calendar_activation_gate import build_calendar_activation_gate
from friday.app.calendar_event_extraction import extract_calendar_event_candidate
from friday.app.calendar_event_write_guard import check_calendar_event_write_allowed
from friday.app.calendar_google_account_store import (
    GOOGLE_CALENDAR_CONNECT_TOKEN,
    build_google_calendar_account,
    google_calendar_account_status,
    save_google_calendar_account,
)
from friday.app.calendar_provider_google import (
    GoogleCalendarProvider,
    build_google_oauth_authorization_url,
    exchange_google_oauth_authorization_response,
)
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


class AccountPolicyCreateRequest(BaseModel):
    provider: str
    label: str
    role: str = "source"
    access: str = "read"
    include_filters: dict[str, Any] | None = None
    exclude_filters: dict[str, Any] | None = None
    notes: str | None = ""
    enabled: bool = True
    approval_token: str


class AccountPolicyUpdateRequest(BaseModel):
    provider: str | None = None
    label: str | None = None
    role: str | None = None
    access: str | None = None
    include_filters: dict[str, Any] | None = None
    exclude_filters: dict[str, Any] | None = None
    notes: str | None = None
    enabled: bool | None = None
    approval_token: str


class PolicyDeleteRequest(BaseModel):
    approval_token: str


class GoogleOAuthUrlRequest(BaseModel):
    client_secrets_path: str


class GoogleOAuthConnectRequest(BaseModel):
    client_secrets_path: str
    authorization_response: str
    approval_token: str
    calendar_id: str = "primary"


class CalendarActivationGateRequest(BaseModel):
    approval_token: str
    scanner_smoke_passed: bool = False


class CalendarEventWriteGuardRequest(BaseModel):
    approval_token: str
    title: str
    start: str
    end: str
    location: str | None = None


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


@app.get("/api/accounts/policies")
def get_account_policies() -> dict[str, Any]:
    policies = list_account_policies()
    main_target = resolve_write_target(policies)
    return _envelope(
        {
            "items": [policy.to_dict() for policy in policies],
            "count": len(policies),
            "ai_context": build_ai_context(policies),
            "main_target": {
                "ok": main_target.ok,
                "policy": main_target.policy.to_dict() if main_target.policy else None,
                "message": main_target.message,
                "blocked_reasons": main_target.blocked_reasons,
            },
            "save_token": POLICY_SAVE_TOKEN,
        }
    )


@app.post("/api/accounts/policies")
def create_policy(payload: AccountPolicyCreateRequest) -> dict[str, Any]:
    try:
        result = create_account_policy(
            provider=payload.provider,
            label=payload.label,
            role=payload.role,
            access=payload.access,
            include_filters=payload.include_filters,
            exclude_filters=payload.exclude_filters,
            notes=payload.notes,
            enabled=payload.enabled,
            approval_token=payload.approval_token,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result.persisted:
        raise HTTPException(status_code=403, detail=result.message)
    return _envelope(
        {
            **result.__dict__,
            "policy": result.policy.to_dict() if result.policy else None,
        }
    )


@app.patch("/api/accounts/policies/{policy_id}")
def update_policy(policy_id: int, payload: AccountPolicyUpdateRequest) -> dict[str, Any]:
    values = payload.dict(exclude={"approval_token"}, exclude_none=True)
    try:
        result = update_account_policy(
            policy_id,
            values=values,
            approval_token=payload.approval_token,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result.persisted:
        raise HTTPException(status_code=403, detail=result.message)
    return _envelope(
        {
            **result.__dict__,
            "policy": result.policy.to_dict() if result.policy else None,
        }
    )


@app.delete("/api/accounts/policies/{policy_id}")
def delete_policy(policy_id: int, payload: PolicyDeleteRequest) -> dict[str, Any]:
    result = delete_account_policy(
        policy_id,
        approval_token=payload.approval_token,
    )
    if not result.persisted:
        raise HTTPException(status_code=403, detail=result.message)
    return _envelope(
        {
            **result.__dict__,
            "policy": result.policy.to_dict() if result.policy else None,
        }
    )


@app.get("/api/accounts/calendar/status")
def get_calendar_account_status() -> dict[str, Any]:
    policies = list_account_policies()
    return _envelope(
        {
            "google": google_calendar_account_status(),
            "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
            "policies": [policy.to_dict() for policy in policies],
            "ai_context": build_ai_context(policies),
        }
    )


@app.post("/api/accounts/calendar/google/oauth-url")
def get_google_calendar_oauth_url(payload: GoogleOAuthUrlRequest) -> dict[str, Any]:
    try:
        preview = build_google_oauth_authorization_url(
            client_secrets_path=payload.client_secrets_path,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _envelope(preview.__dict__)


@app.post("/api/accounts/calendar/google/connect")
def connect_google_calendar_account(payload: GoogleOAuthConnectRequest) -> dict[str, Any]:
    if payload.approval_token != GOOGLE_CALENDAR_CONNECT_TOKEN:
        return _envelope(
            {
                "allowed": False,
                "persisted": False,
                "connected": False,
                "calendar_id": None,
                "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
                "message": "Google-Kalender wurde nicht gespeichert: Token fehlt.",
                "blocked_reasons": ("approval_token_invalid",),
                "external_call_used": False,
            }
        )
    try:
        exchange = exchange_google_oauth_authorization_response(
            client_secrets_path=payload.client_secrets_path,
            authorization_response=payload.authorization_response,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not exchange.ok or exchange.credentials_json is None:
        return _envelope(
            {
                "allowed": False,
                "persisted": False,
                "connected": False,
                "calendar_id": None,
                "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
                "message": exchange.message,
                "blocked_reasons": exchange.blocked_reasons,
                "external_call_used": exchange.external_call_used,
            }
        )
    account = build_google_calendar_account(
        calendar_id=payload.calendar_id,
        credentials_json=exchange.credentials_json,
        last_test_ok=False,
    )
    save_result = save_google_calendar_account(
        account,
        approval_token=payload.approval_token,
    )
    return _envelope(
        {
            "allowed": bool(save_result["allowed"]),
            "persisted": bool(save_result["persisted"]),
            "connected": bool(save_result["persisted"]),
            "calendar_id": account.calendar_id if save_result["persisted"] else None,
            "last_test_ok": False,
            "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
            "message": save_result["message"],
            "blocked_reasons": save_result["blocked_reasons"],
            "external_call_used": exchange.external_call_used,
        }
    )


@app.get("/api/accounts/calendar/google/read-preview")
def get_google_calendar_read_preview(
    range_start: str = Query(...),
    range_end: str = Query(...),
) -> dict[str, Any]:
    account_status = google_calendar_account_status()
    if not account_status["connected"]:
        return _envelope(
            {
                "ok": False,
                "read_only": True,
                "write_enabled": False,
                "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
                "events": [],
                "message": "Kein Google-Kalender-Konto verbunden.",
                "blocked_reasons": ("calendar_account_missing",),
                "external_call_used": False,
            }
        )
    result = GoogleCalendarProvider().list_events(
        range_start=range_start,
        range_end=range_end,
    )
    return _envelope(
        {
            "ok": result.ok,
            "read_only": True,
            "write_enabled": False,
            "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
            "events": [asdict(event) for event in result.events],
            "message": result.message,
            "blocked_reasons": result.blocked_reasons,
            "external_call_used": result.external_call_used,
        }
    )


@app.post("/api/accounts/calendar/activation-gate")
def calendar_activation_gate(payload: CalendarActivationGateRequest) -> dict[str, Any]:
    account_status = google_calendar_account_status()
    gate = build_calendar_activation_gate(
        approval_token=payload.approval_token,
        account_connected=bool(account_status["connected"]),
        connection_test_ok=bool(account_status["last_test_ok"]),
        scanner_smoke_passed=payload.scanner_smoke_passed,
    )
    return _envelope(gate.to_dict())


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
    policies = list_account_policies()
    return _envelope(
        {
            "date": date_value,
            "items": calendar_agent.get_items_for_date(date_value),
            "free_slots": calendar_agent.get_free_slots_for_date(date_value),
            "account_policies": [policy.to_dict() for policy in policies],
            "policy_context": build_ai_context(policies),
            "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
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


@app.post("/api/calendar/events/write-guard")
def preview_calendar_event_write(payload: CalendarEventWriteGuardRequest) -> dict[str, Any]:
    policies = list_account_policies()
    main_target = resolve_write_target(policies)
    account_status = google_calendar_account_status()
    guard = check_calendar_event_write_allowed(
        approval_token=payload.approval_token,
        real_calendar_enabled=config.ENABLE_REAL_CALENDAR,
        main_policy_ok=main_target.ok,
        connection_ok=bool(account_status["last_test_ok"]),
    )
    return _envelope(
        {
            "guard": guard.to_dict(),
            "event_preview": {
                "title": payload.title,
                "start": payload.start,
                "end": payload.end,
                "location": payload.location,
            },
            "main_policy": main_target.policy.to_dict() if main_target.policy else None,
            "provider_event_created": False,
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
