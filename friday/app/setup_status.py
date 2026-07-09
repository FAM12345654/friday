"""Local setup status summary for Friday clients."""

from __future__ import annotations

from friday import config
from friday.app.account_policy_store import list_account_policies
from friday.app.calendar_google_account_store import google_calendar_account_status
from friday.app.email_account_store import email_account_status
from friday.app.local_model_provider import get_local_model_fallback_count
from friday.app.ms_mail_account_store import ms_mail_account_status
from friday.app.whatsapp_inbox_store import get_whatsapp_bridge_status


def build_setup_status() -> dict:
    """Return a read-only setup summary for mobile and API clients."""
    email_status = email_account_status()
    ms_mail_status = ms_mail_account_status()
    whatsapp_status = get_whatsapp_bridge_status()
    google_calendar_status = google_calendar_account_status()
    account_policies = list_account_policies()
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
        "ms_mail": {
            "connected": ms_mail_status["connected"],
            "account_count": ms_mail_status.get("account_count", 0),
            "accounts": ms_mail_status.get("accounts", []),
            "read_enabled": config.ENABLE_MS_MAIL_READ,
            "last_test_ok": ms_mail_status["last_test_ok"],
            "read_only": True,
            "real_email_enabled": config.ENABLE_REAL_EMAIL,
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
            "google": google_calendar_status,
            "policy_count": len(account_policies),
            "enabled_policy_count": len([policy for policy in account_policies if policy.enabled]),
        },
        "safety_flags": {
            "ENABLE_REAL_EMAIL": config.ENABLE_REAL_EMAIL,
            "ENABLE_REAL_WHATSAPP": config.ENABLE_REAL_WHATSAPP,
            "ENABLE_REAL_SMS": config.ENABLE_REAL_SMS,
            "ENABLE_REAL_CALENDAR": config.ENABLE_REAL_CALENDAR,
            "ENABLE_REAL_WEATHER": config.ENABLE_REAL_WEATHER,
            "ENABLE_REAL_MUSIC": config.ENABLE_REAL_MUSIC,
            "ENABLE_MS_MAIL_READ": config.ENABLE_MS_MAIL_READ,
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
                "key": "calendar_accounts",
                "title": "Kalender-Konten",
                "status": "bereit" if google_calendar_status["connected"] or account_policies else "offen",
                "hint": "Google-Kalender braucht OAuth am PC; echtes Schreiben bleibt hart gegatet.",
            },
            {
                "key": "email",
                "title": "E-Mail-Konto",
                "status": "verbunden" if email_status["connected"] else "nicht verbunden",
                "hint": "Echter Versand bleibt deaktiviert.",
            },
            {
                "key": "ms_mail",
                "title": "Familienhelden-Postfach",
                "status": "read-only aktiv" if config.ENABLE_MS_MAIL_READ else "read-only aus",
                "hint": "Microsoft Graph Mail.Read; Senden bleibt deaktiviert.",
            },
            {
                "key": "whatsapp",
                "title": "WhatsApp Read-Bridge",
                "status": "aktiv" if whatsapp_status["read_enabled"] else "aus",
                "hint": "Nur Mitlesen; Senden bleibt Nutzeraktion.",
            },
        ],
    }
