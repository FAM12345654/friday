"""Smoke tests for Friday startup and config values."""

from __future__ import annotations

from pathlib import Path
import importlib

import friday.config as config


def test_modules_import() -> None:
    """All core modules should import without side effects."""
    modules = [
        "friday.main",
        "friday.app.interface",
        "friday.app.menu",
        "friday.app.local_ollama_adapter_preview",
        "friday.app.local_model_provider",
        "friday.app.logic_check_agent",
        "friday.app.model_output_validator",
        "friday.app.ms_mail_account_store",
        "friday.app.ms_mail_provider",
        "friday.app.ms_mail_read_activation_gate",
        "friday.app.imap_mail_account_store",
        "friday.app.imap_mail_read_activation_gate",
        "friday.app.imap_mail_reader",
        "friday.app.obsidian_brain",
        "friday.agents.task_agent",
        "friday.agents.message_agent",
        "friday.agents.calendar_agent",
        "friday.agents.contact_context_agent",
        "friday.agents.approval_agent",
        "friday.agents.morning_briefing_agent",
        "friday.storage.database",
        "friday.storage.repositories",
        "friday.storage.sqlite_storage",
    ]
    for module in modules:
        importlib.import_module(module)


def test_app_name() -> None:
    """Verify the configured public name."""
    assert config.APP_NAME == "Friday"
    assert config.APP_VERSION == "1.0.0"


def test_local_mode() -> None:
    """Ensure the project starts in local mode."""
    assert config.LOCAL_MODE is True


def test_config_safety_flags() -> None:
    """External integrations are intentionally disabled."""
    assert config.ENABLE_REAL_EMAIL is False
    assert config.ENABLE_REAL_SMS is False
    assert config.ENABLE_REAL_WHATSAPP is False
    assert config.ENABLE_REAL_CALENDAR is True
    assert config.ENABLE_REAL_WEATHER is False
    assert config.ENABLE_REAL_MUSIC is False
    assert isinstance(config.ENABLE_MS_MAIL_READ, bool)
    assert config.ENABLE_IMAP_MAIL_READ is False
    assert config.REQUIRE_USER_APPROVAL is True
    assert config.USE_REAL_TODAY is True
    assert config.USE_SQLITE_STORAGE is True
    assert config.DEMO_MODE is False
    assert config.OBSIDIAN_WRITE_ENABLED is False
    assert config.OBSIDIAN_VAULT_PATH == ""
    assert config.OBSIDIAN_ALLOWED_SUBDIR == "Friday"
    assert config.ENABLE_LOCAL_OLLAMA is True
    assert config.OLLAMA_BASE_URL == "http://localhost:11434"
    assert config.OLLAMA_MODEL == "qwen3:8b"
    assert config.OLLAMA_TIMEOUT_SECONDS == 30
    assert config.ENABLE_LOCAL_NOTIFICATIONS is False


def test_demo_date_exists() -> None:
    """Demo date is available for local-first mode."""
    assert isinstance(config.DEMO_DATE, str)
    assert config.DEMO_DATE


def test_database_and_path_settings() -> None:
    """Validate the local data-folder architecture."""
    assert config.LOCAL_DATA_DIR == config.PROJECT_ROOT / "local_data"
    assert config.DATABASE_PATH == config.LOCAL_DATA_DIR / config.DATABASE_NAME
    assert config.DATABASE_PATH == Path(config.PROJECT_ROOT / "local_data" / config.DATABASE_NAME)
    assert config.DEMO_DATABASE_PATH == config.LOCAL_DATA_DIR / config.DEMO_DATABASE_NAME
    assert config.get_database_path() == config.DATABASE_PATH


def test_data_dir_stays_in_package() -> None:
    """Keep JSON seed files in the friday/data package folder."""
    assert config.DATA_DIR == config.PACKAGE_DIR / "data"
