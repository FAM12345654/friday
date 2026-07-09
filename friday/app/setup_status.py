"""Local setup status summary for Friday clients."""

from __future__ import annotations

from friday import config
from friday.app.email_account_store import email_account_status
from friday.app.local_model_provider import get_local_model_fallback_count
from friday.app.whatsapp_inbox_store import get_whatsapp_bridge_status


def build_setup_status() -> dict:
    """Return a read-only setup summary for mobile and API clients."""
    email_status = email_account_status()
    whatsapp_status = get_whatsapp_bridge_status()
    return {
        "app_name": config.APP_NAME,
        "app_version": config.APP_VERSION,
        "local_mode": config.LOCAL_MODE,
        "database": {
            "sqlite": config.USE_SQLITE_STORAGE,
            "path_name": config.get_database_path().name,
        },
        "ai": {
            "local_ollama_enabled": config.ENABLE_LOCAL_OLLAMA,
            "model": config.OLLAMA_MODEL,
            "base_url": config.OLLAMA_BASE_URL,
            "fallback_count": get_local_model_fallback_count(),
            "cloud_fallback_allowed": False,
        },
        "email": {
            "connected": email_status["connected"],
            "real_enabled": config.ENABLE_REAL_EMAIL,
            "last_test_ok": email_status["last_test_ok"],
        },
        "whatsapp": {
            "read_bridge_enabled": whatsapp_status["read_enabled"],
            "real_enabled": config.ENABLE_REAL_WHATSAPP,
            "connected": whatsapp_status["connected"],
            "last_received_at": whatsapp_status["last_received_at"],
        },
        "calendar": {
            "real_enabled": config.ENABLE_REAL_CALENDAR,
            "event_extraction": "python_deterministic_review_only",
            "auto_write_enabled": False,
        },
        "safety_flags": {
            "ENABLE_REAL_EMAIL": config.ENABLE_REAL_EMAIL,
            "ENABLE_REAL_WHATSAPP": config.ENABLE_REAL_WHATSAPP,
            "ENABLE_REAL_SMS": config.ENABLE_REAL_SMS,
            "ENABLE_REAL_CALENDAR": config.ENABLE_REAL_CALENDAR,
            "ENABLE_REAL_WEATHER": config.ENABLE_REAL_WEATHER,
            "ENABLE_REAL_MUSIC": config.ENABLE_REAL_MUSIC,
            "REQUIRE_USER_APPROVAL": config.REQUIRE_USER_APPROVAL,
            "USE_SQLITE_STORAGE": config.USE_SQLITE_STORAGE,
        },
        "setup_steps": [
            {
                "key": "api",
                "title": "Friday API",
                "status": "bereit",
                "hint": "API ist erreichbar, wenn die App verbunden ist.",
            },
            {
                "key": "ai",
                "title": "Lokale KI",
                "status": "aktiv" if config.ENABLE_LOCAL_OLLAMA else "aus",
                "hint": "Nur lokales Ollama, kein Cloud-Fallback.",
            },
            {
                "key": "calendar",
                "title": "Termin-Erkennung",
                "status": "review-only",
                "hint": "Python loest Datum/Zeit deterministisch auf; Nutzer prueft vor dem Speichern.",
            },
            {
                "key": "email",
                "title": "E-Mail-Konto",
                "status": "verbunden" if email_status["connected"] else "nicht verbunden",
                "hint": "Echter Versand bleibt deaktiviert.",
            },
            {
                "key": "whatsapp",
                "title": "WhatsApp Read-Bridge",
                "status": "aktiv" if whatsapp_status["read_enabled"] else "aus",
                "hint": "Nur Mitlesen; Senden bleibt Nutzeraktion.",
            },
        ],
    }
