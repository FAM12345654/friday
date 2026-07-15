"""Tests for the local approval token scanner."""

from __future__ import annotations

from friday.app.approval_token_scanner import (
    evaluate_approval_token_literals,
    iter_python_files,
    scan_paths_for_approval_token_regressions,
    scan_python_source_for_string_literals,
)


def _findings_for_source(source: str, allow_soft_token_values: set[str] | None = None):
    literals = scan_python_source_for_string_literals(source)
    return evaluate_approval_token_literals(
        literals,
        allow_soft_token_values=allow_soft_token_values,
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


def test_approval_token_scanner_passes_expected_tokens() -> None:
    findings = _findings_for_source(_expected_tokens_source())

    assert findings == ()


def test_approval_token_scanner_detects_missing_token() -> None:
    findings = _findings_for_source(
        "\n".join(
            [
                'CONTACT_SAVE_TOKEN = "SPEICHERN"',
                'CONTACT_DELETE_TOKEN = "KONTAKT LÖSCHEN"',
                'FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"',
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
        )
    )

    assert any(
        finding.finding_type == "missing_expected_token"
        and finding.token_key == "obsidian_write"
        for finding in findings
    )


def test_approval_token_scanner_detects_soft_save_token() -> None:
    findings = _findings_for_source(
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
        )
    )

    assert any(
        finding.finding_type == "soft_token_detected"
        and finding.token_value == "ja"
        for finding in findings
    )


def test_approval_token_scanner_detects_soft_obsidian_token() -> None:
    findings = _findings_for_source(
        "\n".join(
            [
                'CONTACT_SAVE_TOKEN = "SPEICHERN"',
                'CONTACT_DELETE_TOKEN = "KONTAKT LÖSCHEN"',
                'FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"',
                'OBSIDIAN_WRITE_TOKEN = "ok"',
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
        )
    )

    assert any(
        finding.finding_type == "soft_token_detected"
        and finding.token_value == "ok"
        for finding in findings
    )


def test_approval_token_scanner_ignores_soft_structural_dict_key() -> None:
    literals = scan_python_source_for_string_literals('payload = {"ok": True}')

    assert not any(literal.value == "ok" for literal in literals)


def test_approval_token_scanner_keeps_soft_approval_mapping_keys() -> None:
    findings = _findings_for_source('approval_map = {"ja": True, "yes": True}')

    assert {finding.token_value for finding in findings if finding.finding_type == "soft_token_detected"} >= {
        "ja",
        "yes",
    }


def test_approval_token_scanner_can_allow_existing_delete_policy_token() -> None:
    findings = _findings_for_source(
        "\n".join(
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
                'DELETE_CONFIRMATION = "JA"',
            ]
        ),
        allow_soft_token_values={"ja"},
    )

    assert not any(
        finding.finding_type == "soft_token_detected"
        and finding.token_value == "JA"
        for finding in findings
    )


def test_scan_paths_for_approval_token_regressions_checks_multiple_files(tmp_path) -> None:
    first_file = tmp_path / "first.py"
    second_file = tmp_path / "second.py"
    first_file.write_text('CONTACT_SAVE_TOKEN = "SPEICHERN"\n', encoding="utf-8")
    second_file.write_text(
        "\n".join(
            [
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
            ]
        ),
        encoding="utf-8",
    )

    result = scan_paths_for_approval_token_regressions([tmp_path])

    assert len(result.checked_files) == 2
    assert result.passed is True
    assert result.findings == ()


def test_approval_token_scan_result_has_safe_flags(tmp_path) -> None:
    tokens_file = tmp_path / "tokens.py"
    tokens_file.write_text(_expected_tokens_source(), encoding="utf-8")

    result = scan_paths_for_approval_token_regressions([tmp_path])

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_approval_token_scanner_detects_missing_forget_person_token() -> None:
    findings = _findings_for_source(
        _expected_tokens_source().replace(
            'FORGET_PERSON_APPROVAL_TOKEN = "PERSON VERGESSEN"\n',
            "",
        )
    )

    assert any(
        finding.finding_type == "missing_expected_token"
        and finding.token_key == "forget_person"
        for finding in findings
    )


def test_iter_python_files_skips_pycache(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    cache_dir = tmp_path / "__pycache__"
    cache_file = cache_dir / "ignored.py"
    safe_file.write_text(_expected_tokens_source(), encoding="utf-8")
    cache_dir.mkdir()
    cache_file.write_text('CONTACT_SAVE_TOKEN = "ja"\n', encoding="utf-8")

    files = iter_python_files([tmp_path])

    assert files == (safe_file,)
