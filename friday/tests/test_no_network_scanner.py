"""Tests for the local no-network scanner."""

from __future__ import annotations

from friday.app.no_network_scanner import (
    iter_python_files,
    scan_paths_for_network_usage,
    scan_python_source_for_network_usage,
)


def _matched_patterns(source: str) -> set[str]:
    return {
        finding.matched_pattern
        for finding in scan_python_source_for_network_usage(source)
    }


def test_no_network_scanner_allows_non_network_calls() -> None:
    findings = scan_python_source_for_network_usage(
        'from pathlib import Path\n\nPath("x").read_text()\n'
    )

    assert findings == ()


def test_no_network_scanner_detects_requests_get() -> None:
    assert _matched_patterns('import requests\nrequests.get("https://example.com")\n') == {
        "requests.get"
    }


def test_no_network_scanner_detects_requests_alias() -> None:
    assert _matched_patterns('import requests as r\nr.post("https://example.com")\n') == {
        "requests.post"
    }


def test_no_network_scanner_detects_httpx_client() -> None:
    assert _matched_patterns("import httpx\nhttpx.Client()\n") == {"httpx.Client"}


def test_no_network_scanner_detects_urllib_from_import() -> None:
    assert _matched_patterns(
        'from urllib.request import urlopen\nurlopen("https://example.com")\n'
    ) == {"urllib.request.urlopen"}


def test_no_network_scanner_allows_local_ollama_runtime_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        'from urllib import request\nrequest.urlopen("http://127.0.0.1:11434/api/tags")\n',
        file_path="friday/app/local_ollama_runtime.py",
    )

    assert findings == ()


def test_no_network_scanner_allows_email_sender_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        "import smtplib\nsmtplib.SMTP_SSL('smtp.example.test', 465)\n",
        file_path="friday/app/email_smtp_sender.py",
    )

    assert findings == ()


def test_no_network_scanner_blocks_smtp_outside_sender_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        "import smtplib\nsmtplib.SMTP_SSL('smtp.example.test', 465)\n",
        file_path="friday/app/unsafe.py",
    )

    assert {finding.matched_pattern for finding in findings} == {"smtplib.SMTP_SSL"}


def test_no_network_scanner_allows_imap_reader_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        "import imaplib\nimaplib.IMAP4_SSL('imap.example.test', 993)\n",
        file_path="friday/app/email_imap_reader.py",
    )

    assert findings == ()


def test_no_network_scanner_allows_google_provider_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        "import socket\nsocket.socket()\n",
        file_path="friday/app/calendar_provider_google.py",
    )

    assert findings == ()


def test_no_network_scanner_allows_ics_provider_urllib_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        'from urllib import request\nrequest.urlopen("https://example.invalid/calendar.ics")\n',
        file_path="friday/app/calendar_provider_ics.py",
    )

    assert findings == ()


def test_no_network_scanner_allows_ms_mail_provider_urllib_allowlist() -> None:
    findings = scan_python_source_for_network_usage(
        'from urllib import request\nrequest.urlopen("https://graph.microsoft.com/v1.0/me")\n',
        file_path="friday/app/ms_mail_provider.py",
    )

    assert findings == ()


def test_no_network_scanner_blocks_urllib_outside_ics_provider() -> None:
    findings = scan_python_source_for_network_usage(
        'from urllib import request\nrequest.urlopen("https://example.invalid/calendar.ics")\n',
        file_path="friday/app/unsafe_calendar_fetch.py",
    )

    assert {finding.matched_pattern for finding in findings} == {"urllib.request.urlopen"}


def test_no_network_scanner_detects_socket() -> None:
    assert _matched_patterns("import socket\nsocket.socket()\n") == {"socket.socket"}


def test_no_network_scanner_detects_aiohttp_client_session() -> None:
    assert _matched_patterns("import aiohttp\naiohttp.ClientSession()\n") == {
        "aiohttp.ClientSession"
    }


def test_no_network_scanner_detects_websockets_connect() -> None:
    assert _matched_patterns(
        'import websockets\nwebsockets.connect("wss://example.com")\n'
    ) == {"websockets.connect"}


def test_scan_paths_for_network_usage_checks_multiple_files(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    blocked_file = tmp_path / "blocked.py"
    safe_file.write_text('from pathlib import Path\nPath("x")\n', encoding="utf-8")
    blocked_file.write_text(
        'import requests\nrequests.get("https://example.com")\n',
        encoding="utf-8",
    )

    result = scan_paths_for_network_usage([tmp_path])

    assert len(result.checked_files) == 2
    assert result.passed is False
    assert result.findings[0].matched_pattern == "requests.get"


def test_no_network_scan_result_has_safe_flags(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    safe_file.write_text("value = 1\n", encoding="utf-8")

    result = scan_paths_for_network_usage([tmp_path])

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_iter_python_files_skips_pycache(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    cache_dir = tmp_path / "__pycache__"
    cache_file = cache_dir / "ignored.py"
    safe_file.write_text("value = 1\n", encoding="utf-8")
    cache_dir.mkdir()
    cache_file.write_text("import requests\nrequests.get('x')\n", encoding="utf-8")

    files = iter_python_files([tmp_path])

    assert files == (safe_file,)
