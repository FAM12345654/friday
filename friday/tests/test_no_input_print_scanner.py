"""Tests for the local no-input/print scanner."""

from __future__ import annotations

from friday.app.no_input_print_scanner import (
    iter_python_files,
    scan_paths_for_input_print,
    scan_python_source_for_input_print,
)


def _blocked_names(source: str) -> set[str]:
    return {
        finding.blocked_name
        for finding in scan_python_source_for_input_print(source)
    }


def test_no_input_print_scanner_allows_safe_code() -> None:
    findings = scan_python_source_for_input_print(
        'value = "Projekt Alpha"\nnormalized = value.strip().lower()\n'
    )

    assert findings == ()


def test_no_input_print_scanner_detects_input_call() -> None:
    assert _blocked_names('name = input("Name: ")\n') == {"input"}


def test_no_input_print_scanner_detects_print_call() -> None:
    assert _blocked_names('print("Hallo")\n') == {"print"}


def test_no_input_print_scanner_detects_builtins_input() -> None:
    assert _blocked_names('import builtins\nbuiltins.input("Name: ")\n') == {
        "builtins.input"
    }


def test_no_input_print_scanner_detects_builtins_print_alias() -> None:
    assert _blocked_names(
        'from builtins import print as output\noutput("Hallo")\n'
    ) == {"builtins.print"}


def test_no_input_print_scanner_detects_builtins_input_alias() -> None:
    assert _blocked_names(
        'from builtins import input as read_input\nread_input("Name: ")\n'
    ) == {"builtins.input"}


def test_scan_paths_for_input_print_checks_multiple_files(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    blocked_file = tmp_path / "blocked.py"
    safe_file.write_text('value = "Projekt Alpha"\n', encoding="utf-8")
    blocked_file.write_text('print("Hallo")\n', encoding="utf-8")

    result = scan_paths_for_input_print([tmp_path])

    assert len(result.checked_files) == 2
    assert result.passed is False
    assert result.findings[0].blocked_name == "print"


def test_scan_paths_for_input_print_respects_excluded_file_paths(tmp_path) -> None:
    blocked_file = tmp_path / "interface.py"
    blocked_file.write_text('print("Hallo")\n', encoding="utf-8")

    result = scan_paths_for_input_print(
        [tmp_path],
        excluded_file_paths=(blocked_file,),
    )

    assert result.checked_files == ()
    assert result.findings == ()
    assert result.passed is True


def test_no_input_print_scan_result_has_safe_flags(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    safe_file.write_text("value = 1\n", encoding="utf-8")

    result = scan_paths_for_input_print([tmp_path])

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_iter_python_files_skips_pycache(tmp_path) -> None:
    safe_file = tmp_path / "safe.py"
    cache_dir = tmp_path / "__pycache__"
    cache_file = cache_dir / "ignored.py"
    safe_file.write_text("value = 1\n", encoding="utf-8")
    cache_dir.mkdir()
    cache_file.write_text('print("ignore")\n', encoding="utf-8")

    files = iter_python_files([tmp_path])

    assert files == (safe_file,)
