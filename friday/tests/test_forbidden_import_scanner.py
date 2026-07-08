"""Tests for the local forbidden import scanner."""

from __future__ import annotations

from friday.app.forbidden_import_scanner import (
    FORBIDDEN_IMPORT_ROOTS,
    scan_python_paths_for_forbidden_imports,
    scan_python_source_for_forbidden_imports,
)


def test_forbidden_import_scanner_allows_safe_standard_imports() -> None:
    result = scan_python_source_for_forbidden_imports(
        "import ast\nfrom pathlib import Path\n",
    )

    assert result.passed is True
    assert result.findings == ()


def test_forbidden_import_scanner_blocks_plain_forbidden_import() -> None:
    result = scan_python_source_for_forbidden_imports("import requests\n")

    assert result.passed is False
    assert len(result.findings) == 1
    assert result.findings[0].module == "requests"
    assert result.findings[0].line == 1


def test_forbidden_import_scanner_blocks_from_import() -> None:
    result = scan_python_source_for_forbidden_imports("from openai import OpenAI\n")

    assert result.passed is False
    assert result.findings[0].module == "openai"
    assert result.findings[0].import_name == "openai"


def test_forbidden_import_scanner_blocks_nested_import_root() -> None:
    result = scan_python_source_for_forbidden_imports(
        "import googleapiclient.discovery\n",
    )

    assert result.passed is False
    assert result.findings[0].module == "googleapiclient"
    assert result.findings[0].import_name == "googleapiclient.discovery"


def test_forbidden_import_scanner_reports_multiple_findings() -> None:
    result = scan_python_source_for_forbidden_imports(
        "import requests\nfrom twilio.rest import Client\nimport socket\n",
    )

    modules = {finding.module for finding in result.findings}
    assert result.passed is False
    assert modules == {"requests", "twilio", "socket"}


def test_forbidden_import_scanner_scans_paths(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    blocked_file = tmp_path / "blocked.py"
    safe_file.write_text("import dataclasses\n", encoding="utf-8")
    blocked_file.write_text("import httpx\n", encoding="utf-8")

    result = scan_python_paths_for_forbidden_imports([tmp_path])

    assert len(result.scanned_files) == 2
    assert result.passed is False
    assert result.findings[0].module == "httpx"


def test_forbidden_import_scanner_has_safe_flags() -> None:
    result = scan_python_source_for_forbidden_imports("import ast\n")

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_forbidden_import_roots_include_expected_entries() -> None:
    expected = {"openai", "requests", "httpx", "twilio", "socket"}

    assert expected.issubset(set(FORBIDDEN_IMPORT_ROOTS))
