"""Local safety flag regression scanner.

The scanner reads Python files and checks expected safety flag assignments via AST.
It does not execute scanned files.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


SafetyFlagFindingType = Literal[
    "missing_flag",
    "unexpected_value",
    "non_literal_value",
    "duplicate_conflict",
]

EXPECTED_SAFETY_FLAGS: dict[str, bool] = {
    "LOCAL_MODE": True,
    "ENABLE_REAL_EMAIL": False,
    "ENABLE_REAL_WHATSAPP": False,
    "ENABLE_REAL_SMS": False,
    # Bewusst aktivierte Ausnahme: echte Kalender-Writes bleiben pro Event
    # durch KALENDER AKTIVIEREN + TERMIN SPEICHERN + Policy + Verbindung gegatet.
    "ENABLE_REAL_CALENDAR": True,
    "ENABLE_REAL_WEATHER": False,
    "ENABLE_REAL_MUSIC": False,
    "ENABLE_MS_MAIL_READ": False,
    "REQUIRE_USER_APPROVAL": True,
    "USE_REAL_TODAY": True,
    "USE_SQLITE_STORAGE": True,
    "OBSIDIAN_WRITE_ENABLED": False,
    "ENABLE_LOCAL_OLLAMA": True,
}

DEFAULT_EXCLUDED_PATH_PARTS: tuple[str, ...] = (
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
)


@dataclass(frozen=True)
class SafetyFlagAssignment:
    """One assignment to a known safety flag."""

    file_path: str
    line_number: int
    flag_name: str
    value: bool | None
    literal: bool


@dataclass(frozen=True)
class SafetyFlagFinding:
    """One safety flag regression finding."""

    file_path: str | None
    line_number: int | None
    flag_name: str
    expected_value: bool
    actual_value: bool | None
    finding_type: SafetyFlagFindingType
    message: str


@dataclass(frozen=True)
class SafetyFlagRegressionScanResult:
    """Result of scanning local Python files for safety flag regressions."""

    checked_files: tuple[str, ...]
    assignments: tuple[SafetyFlagAssignment, ...]
    findings: tuple[SafetyFlagFinding, ...]
    passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _literal_bool(node: ast.AST) -> tuple[bool | None, bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value, True
    return None, False


def _target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def scan_python_source_for_safety_flags(
    source: str,
    file_path: str = "<memory>",
    expected_flags: dict[str, bool] | None = None,
) -> tuple[SafetyFlagAssignment, ...]:
    """Scan source text for assignments to expected safety flags."""
    expected = expected_flags or EXPECTED_SAFETY_FLAGS
    tree = ast.parse(source, filename=file_path)
    assignments: list[SafetyFlagAssignment] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            value, literal = _literal_bool(node.value)
            for target in node.targets:
                name = _target_name(target)
                if name in expected:
                    assignments.append(
                        SafetyFlagAssignment(
                            file_path=file_path,
                            line_number=node.lineno,
                            flag_name=name,
                            value=value,
                            literal=literal,
                        )
                    )

        if isinstance(node, ast.AnnAssign):
            name = _target_name(node.target)
            if name in expected:
                value, literal = (
                    _literal_bool(node.value) if node.value is not None else (None, False)
                )
                assignments.append(
                    SafetyFlagAssignment(
                        file_path=file_path,
                        line_number=node.lineno,
                        flag_name=name,
                        value=value,
                        literal=literal,
                    )
                )

    return tuple(assignments)


def evaluate_safety_flag_assignments(
    assignments: Iterable[SafetyFlagAssignment],
    expected_flags: dict[str, bool] | None = None,
) -> tuple[SafetyFlagFinding, ...]:
    """Evaluate collected safety flag assignments against expected values."""
    expected = expected_flags or EXPECTED_SAFETY_FLAGS
    by_flag: dict[str, list[SafetyFlagAssignment]] = {flag: [] for flag in expected}

    for assignment in assignments:
        if assignment.flag_name in by_flag:
            by_flag[assignment.flag_name].append(assignment)

    findings: list[SafetyFlagFinding] = []

    for flag_name, expected_value in expected.items():
        flag_assignments = by_flag.get(flag_name, [])

        if not flag_assignments:
            findings.append(
                SafetyFlagFinding(
                    file_path=None,
                    line_number=None,
                    flag_name=flag_name,
                    expected_value=expected_value,
                    actual_value=None,
                    finding_type="missing_flag",
                    message=f"{flag_name} is missing.",
                )
            )
            continue

        for assignment in flag_assignments:
            if not assignment.literal:
                findings.append(
                    SafetyFlagFinding(
                        file_path=assignment.file_path,
                        line_number=assignment.line_number,
                        flag_name=flag_name,
                        expected_value=expected_value,
                        actual_value=None,
                        finding_type="non_literal_value",
                        message=f"{flag_name} is not assigned a bool literal.",
                    )
                )
                continue

            if assignment.value != expected_value:
                findings.append(
                    SafetyFlagFinding(
                        file_path=assignment.file_path,
                        line_number=assignment.line_number,
                        flag_name=flag_name,
                        expected_value=expected_value,
                        actual_value=assignment.value,
                        finding_type="unexpected_value",
                        message=f"{flag_name} expected {expected_value!r}, got {assignment.value!r}.",
                    )
                )

        literal_values = {
            assignment.value for assignment in flag_assignments if assignment.literal
        }
        if len(literal_values) > 1:
            first = flag_assignments[0]
            findings.append(
                SafetyFlagFinding(
                    file_path=first.file_path,
                    line_number=first.line_number,
                    flag_name=flag_name,
                    expected_value=expected_value,
                    actual_value=None,
                    finding_type="duplicate_conflict",
                    message=f"{flag_name} has conflicting assignments.",
                )
            )

    return tuple(findings)


def scan_python_file_for_safety_flags(
    file_path: str | Path,
    expected_flags: dict[str, bool] | None = None,
) -> tuple[SafetyFlagAssignment, ...]:
    """Scan one local Python file for safety flag assignments."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    return scan_python_source_for_safety_flags(
        source,
        file_path=str(path),
        expected_flags=expected_flags,
    )


def iter_python_files(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
) -> tuple[Path, ...]:
    """Return Python files below root paths, skipping excluded path parts."""
    files: list[Path] = []

    for root in roots:
        root_path = Path(root)
        if root_path.is_file() and root_path.suffix == ".py":
            candidate_files = (root_path,)
        elif root_path.is_dir():
            candidate_files = tuple(root_path.rglob("*.py"))
        else:
            candidate_files = ()

        for candidate in candidate_files:
            if any(part in candidate.parts for part in excluded_path_parts):
                continue
            files.append(candidate)

    return tuple(sorted(set(files)))


def scan_paths_for_safety_flag_regressions(
    roots: Iterable[str | Path],
    expected_flags: dict[str, bool] | None = None,
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
) -> SafetyFlagRegressionScanResult:
    """Scan paths for safety flag regressions."""
    python_files = iter_python_files(roots, excluded_path_parts=excluded_path_parts)
    checked_files: list[str] = []
    assignments: list[SafetyFlagAssignment] = []

    for file_path in python_files:
        checked_files.append(str(file_path))
        assignments.extend(
            scan_python_file_for_safety_flags(
                file_path,
                expected_flags=expected_flags,
            )
        )

    findings = evaluate_safety_flag_assignments(
        assignments,
        expected_flags=expected_flags,
    )

    return SafetyFlagRegressionScanResult(
        checked_files=tuple(checked_files),
        assignments=tuple(assignments),
        findings=findings,
        passed=not findings,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
