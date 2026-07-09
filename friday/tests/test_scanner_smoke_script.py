"""Tests for the local Friday safety smoke runner."""

from __future__ import annotations

from friday.app.safety_flag_regression_scanner import EXPECTED_SAFETY_FLAGS
from friday.app.safety_smoke_runner import (
    DEFAULT_APPROVAL_TOKEN_EXCLUDED_FILES,
    DEFAULT_INPUT_PRINT_EXCLUDED_FILES,
    DEFAULT_SCAN_ROOTS,
    SAFETY_SMOKE_CHECK_NAMES,
    format_safety_smoke_result,
    run_safety_smoke,
)


def _expected_flags_source() -> str:
    return "\n".join(
        f"{flag_name} = {value!r}"
        for flag_name, value in EXPECTED_SAFETY_FLAGS.items()
    )


def _expected_tokens_source() -> str:
    return "\n".join(
        [
            'CONTACT_SAVE_TOKEN = "SPEICHERN"',
            'CONTACT_DELETE_TOKEN = "KONTAKT LÖSCHEN"',
            'FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"',
            'OBSIDIAN_WRITE_TOKEN = "OBSIDIAN SCHREIBEN"',
            'BACKUP_WRITE_APPROVAL_TOKEN = "BACKUP ERSTELLEN"',
            'RESTORE_WRITE_APPROVAL_TOKEN = "RESTORE AUSFUEHREN"',
            'LOCAL_DATA_EXPORT_APPROVAL_TOKEN = "DATEN EXPORTIEREN"',
            'REVIEW_EXPORT_APPROVAL_TOKEN = "REVIEW EXPORTIEREN"',
            'LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN = "IMPORT ANWENDEN"',
            'EXPORT_CLEANUP_TOKEN = "EXPORT AUFRAEUMEN"',
            'BACKUP_CLEANUP_TOKEN = "BACKUP AUFRAEUMEN"',
            'RESTORE_CLEANUP_TOKEN = "RESTORE AUFRAEUMEN"',
            'REVIEW_CLEANUP_TOKEN = "REVIEW AUFRAEUMEN"',
            'SELF_BUILDING_COMMIT_APPROVAL_TOKEN = "COMMIT ERSTELLEN"',
            'EMAIL_ACCOUNT_SAVE_TOKEN = "KONTO SPEICHERN"',
            'EMAIL_ACCOUNT_DELETE_TOKEN = "KONTO LOESCHEN"',
            'EMAIL_ACTIVATION_TOKEN = "EMAIL AKTIVIEREN"',
            'EMAIL_SEND_TOKEN = "EMAIL SENDEN"',
            'WHATSAPP_BRIDGE_ACTIVATION_TOKEN = "WHATSAPP BRIDGE AKTIVIEREN"',
            'CALENDAR_EVENT_SAVE_TOKEN = "TERMIN SPEICHERN"',
            'CALENDAR_EVENT_DELETE_TOKEN = "TERMIN LOESCHEN"',
            'CALENDAR_EVENT_SAVE_TOKEN = "TERMIN SPEICHERN"',
            'CALENDAR_EVENT_DELETE_TOKEN = "TERMIN LOESCHEN"',
        ]
    )


def _write_clean_project(tmp_path) -> None:
    (tmp_path / "flags.py").write_text(_expected_flags_source(), encoding="utf-8")
    (tmp_path / "tokens.py").write_text(_expected_tokens_source(), encoding="utf-8")
    (tmp_path / "safe.py").write_text("VALUE = 1\n", encoding="utf-8")


def _check_by_name(result, name: str):
    return next(check for check in result.checks if check.name == name)


def test_safety_smoke_runner_passes_clean_temp_project(tmp_path) -> None:
    _write_clean_project(tmp_path)

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is True
    assert all(check.passed for check in result.checks)


def test_safety_smoke_runner_fails_for_forbidden_import(tmp_path) -> None:
    _write_clean_project(tmp_path)
    (tmp_path / "bad_import.py").write_text("import requests\n", encoding="utf-8")

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is False
    assert _check_by_name(result, "forbidden_imports").passed is False


def test_safety_smoke_runner_fails_for_network_call(tmp_path) -> None:
    _write_clean_project(tmp_path)
    (tmp_path / "bad_network.py").write_text(
        "import requests\nrequests.get('https://example.test')\n",
        encoding="utf-8",
    )

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is False
    assert _check_by_name(result, "no_network").passed is False


def test_safety_smoke_runner_fails_for_input_print(tmp_path) -> None:
    _write_clean_project(tmp_path)
    (tmp_path / "bad_print.py").write_text("print('hello')\n", encoding="utf-8")

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is False
    assert _check_by_name(result, "no_input_print").passed is False


def test_safety_smoke_runner_fails_for_safety_flag_regression(tmp_path) -> None:
    _write_clean_project(tmp_path)
    (tmp_path / "flags.py").write_text(
        _expected_flags_source().replace("ENABLE_REAL_EMAIL = False", "ENABLE_REAL_EMAIL = True"),
        encoding="utf-8",
    )

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is False
    assert _check_by_name(result, "safety_flags").passed is False


def test_safety_smoke_runner_fails_for_soft_approval_token(tmp_path) -> None:
    _write_clean_project(tmp_path)
    (tmp_path / "tokens.py").write_text(
        "\n".join(
            [
                'CONTACT_SAVE_TOKEN = "ja"',
                'CONTACT_DELETE_TOKEN = "KONTAKT LÖSCHEN"',
                'FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"',
                'OBSIDIAN_WRITE_TOKEN = "OBSIDIAN SCHREIBEN"',
                'BACKUP_WRITE_APPROVAL_TOKEN = "BACKUP ERSTELLEN"',
                'RESTORE_WRITE_APPROVAL_TOKEN = "RESTORE AUSFUEHREN"',
                'LOCAL_DATA_EXPORT_APPROVAL_TOKEN = "DATEN EXPORTIEREN"',
                'REVIEW_EXPORT_APPROVAL_TOKEN = "REVIEW EXPORTIEREN"',
                'LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN = "IMPORT ANWENDEN"',
                'EXPORT_CLEANUP_TOKEN = "EXPORT AUFRAEUMEN"',
                'BACKUP_CLEANUP_TOKEN = "BACKUP AUFRAEUMEN"',
                'RESTORE_CLEANUP_TOKEN = "RESTORE AUFRAEUMEN"',
                'REVIEW_CLEANUP_TOKEN = "REVIEW AUFRAEUMEN"',
                'SELF_BUILDING_COMMIT_APPROVAL_TOKEN = "COMMIT ERSTELLEN"',
            ]
        ),
        encoding="utf-8",
    )

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.passed is False
    assert _check_by_name(result, "approval_tokens").passed is False


def test_safety_smoke_runner_uses_release_check_order(tmp_path) -> None:
    _write_clean_project(tmp_path)

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert tuple(check.name for check in result.checks) == SAFETY_SMOKE_CHECK_NAMES


def test_safety_smoke_runner_defaults_are_release_pinned() -> None:
    assert DEFAULT_SCAN_ROOTS == (
        "friday/app",
        "friday/agents",
        "friday/storage",
        "friday/config.py",
    )
    assert DEFAULT_INPUT_PRINT_EXCLUDED_FILES == (
        "friday/agents/approval_agent.py",
        "friday/app/interface.py",
        "friday/app/menu.py",
    )
    assert DEFAULT_APPROVAL_TOKEN_EXCLUDED_FILES == (
        "friday/agents/message_agent.py",
        "friday/app/approval_token_scanner.py",
    )


def test_format_safety_smoke_result(tmp_path) -> None:
    _write_clean_project(tmp_path)
    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    output = format_safety_smoke_result(result)

    assert "Friday Safety Smoke Result:" in output
    assert "Overall: PASS" in output


def test_safety_smoke_result_has_safe_flags(tmp_path) -> None:
    _write_clean_project(tmp_path)

    result = run_safety_smoke(roots=(tmp_path,), input_print_excluded_files=())

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
