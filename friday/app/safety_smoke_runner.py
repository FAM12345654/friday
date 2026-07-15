"""Local Friday safety smoke runner.

Runs local safety scanners without executing scanned files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from friday import config
from friday.app.approval_token_scanner import (
    iter_python_files as iter_approval_python_files,
    scan_paths_for_approval_token_regressions,
)
from friday.app.forbidden_import_scanner import scan_python_paths_for_forbidden_imports
from friday.app.no_input_print_scanner import scan_paths_for_input_print
from friday.app.no_network_scanner import scan_paths_for_network_usage
from friday.app.safety_flag_regression_scanner import (
    EXPECTED_SAFETY_FLAGS,
    scan_paths_for_safety_flag_regressions,
)


DEFAULT_SCAN_ROOTS: tuple[str, ...] = (
    "friday/app",
    "friday/agents",
    "friday/storage",
    "friday/config.py",
)
DEFAULT_INPUT_PRINT_EXCLUDED_FILES: tuple[str, ...] = (
    "friday/agents/approval_agent.py",
    "friday/app/interface.py",
    "friday/app/menu.py",
)
DEFAULT_APPROVAL_TOKEN_EXCLUDED_FILES: tuple[str, ...] = (
    "friday/agents/message_agent.py",
    "friday/app/approval_token_scanner.py",
)
SAFETY_SMOKE_CHECK_NAMES: tuple[str, ...] = (
    "forbidden_imports",
    "no_network",
    "no_input_print",
    "safety_flags",
    "approval_tokens",
)


@dataclass(frozen=True)
class SafetySmokeCheckResult:
    """One safety smoke check result."""

    name: str
    passed: bool
    findings_count: int


@dataclass(frozen=True)
class SafetySmokeResult:
    """Combined safety smoke result."""

    checks: tuple[SafetySmokeCheckResult, ...]
    passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def run_safety_smoke(
    roots: Iterable[str | Path] = DEFAULT_SCAN_ROOTS,
    input_print_excluded_files: tuple[str | Path, ...] = DEFAULT_INPUT_PRINT_EXCLUDED_FILES,
    approval_token_excluded_files: tuple[
        str | Path, ...
    ] = DEFAULT_APPROVAL_TOKEN_EXCLUDED_FILES,
    safety_flag_overrides: dict[str, bool] | None = None,
) -> SafetySmokeResult:
    """Run all local safety scanners and return a structured result."""
    def _resolve_path(path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return config.PROJECT_ROOT / candidate

    roots_tuple = tuple(_resolve_path(path) for path in roots)
    input_print_excluded_paths = tuple(
        _resolve_path(path) for path in input_print_excluded_files
    )
    excluded_approval_paths = {
        _resolve_path(path) for path in approval_token_excluded_files
    }
    approval_scan_files = tuple(
        file_path
        for file_path in iter_approval_python_files(roots_tuple)
        if file_path not in excluded_approval_paths
    )

    forbidden_imports = scan_python_paths_for_forbidden_imports(roots_tuple)
    no_network = scan_paths_for_network_usage(roots_tuple)
    no_input_print = scan_paths_for_input_print(
        roots_tuple,
        excluded_file_paths=input_print_excluded_paths,
    )
    expected_safety_flags = dict(EXPECTED_SAFETY_FLAGS)
    expected_safety_flags.update(safety_flag_overrides or {})
    safety_flags = scan_paths_for_safety_flag_regressions(
        roots_tuple,
        expected_flags=expected_safety_flags,
    )
    approval_tokens = scan_paths_for_approval_token_regressions(
        approval_scan_files,
        allow_soft_token_values={"ja"},
    )

    checks = (
        SafetySmokeCheckResult(
            name="forbidden_imports",
            passed=forbidden_imports.passed,
            findings_count=len(forbidden_imports.findings),
        ),
        SafetySmokeCheckResult(
            name="no_network",
            passed=no_network.passed,
            findings_count=len(no_network.findings),
        ),
        SafetySmokeCheckResult(
            name="no_input_print",
            passed=no_input_print.passed,
            findings_count=len(no_input_print.findings),
        ),
        SafetySmokeCheckResult(
            name="safety_flags",
            passed=safety_flags.passed,
            findings_count=len(safety_flags.findings),
        ),
        SafetySmokeCheckResult(
            name="approval_tokens",
            passed=approval_tokens.passed,
            findings_count=len(approval_tokens.findings),
        ),
    )

    return SafetySmokeResult(
        checks=checks,
        passed=all(check.passed for check in checks),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def format_safety_smoke_result(result: SafetySmokeResult) -> str:
    """Format a safety smoke result for CLI output."""
    lines = ["Friday Safety Smoke Result:"]

    for check in result.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"- {check.name}: {status} ({check.findings_count} findings)")

    lines.append(f"Overall: {'PASS' if result.passed else 'FAIL'}")
    return "\n".join(lines)
