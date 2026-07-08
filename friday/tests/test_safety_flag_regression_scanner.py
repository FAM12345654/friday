"""Tests for the local safety flag regression scanner."""

from __future__ import annotations

from friday.app.safety_flag_regression_scanner import (
    EXPECTED_SAFETY_FLAGS,
    evaluate_safety_flag_assignments,
    iter_python_files,
    scan_paths_for_safety_flag_regressions,
    scan_python_source_for_safety_flags,
)


def _expected_flags_source(overrides: dict[str, str] | None = None) -> str:
    overrides = overrides or {}
    lines = []
    for flag_name, expected_value in EXPECTED_SAFETY_FLAGS.items():
        value = overrides.get(flag_name, repr(expected_value))
        lines.append(f"{flag_name} = {value}")
    return "\n".join(lines) + "\n"


def _findings_for_source(source: str):
    assignments = scan_python_source_for_safety_flags(source)
    return evaluate_safety_flag_assignments(assignments)


def test_safety_flag_scanner_passes_expected_flags() -> None:
    findings = _findings_for_source(_expected_flags_source())

    assert findings == ()


def test_safety_flag_scanner_detects_email_enabled() -> None:
    findings = _findings_for_source(
        _expected_flags_source({"ENABLE_REAL_EMAIL": "True"})
    )

    assert any(
        finding.finding_type == "unexpected_value"
        and finding.flag_name == "ENABLE_REAL_EMAIL"
        and finding.expected_value is False
        and finding.actual_value is True
        for finding in findings
    )


def test_safety_flag_scanner_detects_obsidian_write_enabled() -> None:
    findings = _findings_for_source(
        _expected_flags_source({"OBSIDIAN_WRITE_ENABLED": "True"})
    )

    assert any(
        finding.finding_type == "unexpected_value"
        and finding.flag_name == "OBSIDIAN_WRITE_ENABLED"
        and finding.expected_value is False
        and finding.actual_value is True
        for finding in findings
    )


def test_safety_flag_scanner_detects_local_ollama_enabled() -> None:
    findings = _findings_for_source(
        _expected_flags_source({"ENABLE_LOCAL_OLLAMA": "True"})
    )

    assert any(
        finding.finding_type == "unexpected_value"
        and finding.flag_name == "ENABLE_LOCAL_OLLAMA"
        and finding.expected_value is False
        and finding.actual_value is True
        for finding in findings
    )


def test_safety_flag_scanner_detects_missing_flag() -> None:
    source = "\n".join(
        f"{flag_name} = {value!r}"
        for flag_name, value in EXPECTED_SAFETY_FLAGS.items()
        if flag_name != "ENABLE_REAL_SMS"
    )
    findings = _findings_for_source(source)

    assert any(
        finding.finding_type == "missing_flag"
        and finding.flag_name == "ENABLE_REAL_SMS"
        for finding in findings
    )


def test_safety_flag_scanner_detects_non_literal_value() -> None:
    findings = _findings_for_source(
        _expected_flags_source({"ENABLE_REAL_EMAIL": 'bool(os.getenv("ENABLE_REAL_EMAIL"))'})
    )

    assert any(
        finding.finding_type == "non_literal_value"
        and finding.flag_name == "ENABLE_REAL_EMAIL"
        for finding in findings
    )


def test_safety_flag_scanner_detects_duplicate_conflict() -> None:
    source = _expected_flags_source() + "ENABLE_REAL_EMAIL = True\n"
    findings = _findings_for_source(source)

    finding_types = {finding.finding_type for finding in findings}
    assert "unexpected_value" in finding_types
    assert "duplicate_conflict" in finding_types


def test_scan_paths_for_safety_flag_regressions_checks_multiple_files(tmp_path) -> None:
    flags = list(EXPECTED_SAFETY_FLAGS.items())
    first_file = tmp_path / "first.py"
    second_file = tmp_path / "second.py"
    first_file.write_text(
        "\n".join(f"{name} = {value!r}" for name, value in flags[:4]),
        encoding="utf-8",
    )
    second_file.write_text(
        "\n".join(f"{name} = {value!r}" for name, value in flags[4:]),
        encoding="utf-8",
    )

    result = scan_paths_for_safety_flag_regressions([tmp_path])

    assert len(result.checked_files) == 2
    assert result.passed is True
    assert result.findings == ()


def test_safety_flag_scan_result_has_safe_flags(tmp_path) -> None:
    flags_file = tmp_path / "flags.py"
    flags_file.write_text(_expected_flags_source(), encoding="utf-8")

    result = scan_paths_for_safety_flag_regressions([tmp_path])

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_iter_python_files_skips_pycache(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    cache_dir = tmp_path / "__pycache__"
    cache_file = cache_dir / "ignored.py"
    safe_file.write_text(_expected_flags_source(), encoding="utf-8")
    cache_dir.mkdir()
    cache_file.write_text("ENABLE_REAL_EMAIL = True\n", encoding="utf-8")

    files = iter_python_files([tmp_path])

    assert files == (safe_file,)
