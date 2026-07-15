"""Local approval token scanner.

The scanner reads Python files and checks approval-token usage via AST.
It does not execute scanned files.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


ApprovalTokenFindingType = Literal[
    "missing_expected_token",
    "soft_token_detected",
]

EXPECTED_APPROVAL_TOKENS: dict[str, str] = {
    "contact_save": "SPEICHERN",
    "contact_delete": "KONTAKT LÖSCHEN",
    "forget_person": "PERSON VERGESSEN",
    "obsidian_write": "OBSIDIAN SCHREIBEN",
    "backup_write": "BACKUP ERSTELLEN",
    "restore_write": "RESTORE AUSFUEHREN",
    "local_data_export": "DATEN EXPORTIEREN",
    "review_export": "REVIEW EXPORTIEREN",
    "local_data_import_apply": "IMPORT ANWENDEN",
    "export_cleanup": "EXPORT AUFRAEUMEN",
    "backup_cleanup": "BACKUP AUFRAEUMEN",
    "restore_cleanup": "RESTORE AUFRAEUMEN",
    "review_cleanup": "REVIEW AUFRAEUMEN",
    "self_building_commit": "COMMIT ERSTELLEN",
    "email_account_save": "KONTO SPEICHERN",
    "email_account_delete": "KONTO LOESCHEN",
    "email_real_activation": "EMAIL AKTIVIEREN",
    "email_send": "EMAIL SENDEN",
    "whatsapp_bridge_read_activation": "WHATSAPP BRIDGE AKTIVIEREN",
    "calendar_event_save": "TERMIN SPEICHERN",
    "calendar_event_delete": "TERMIN LOESCHEN",
}

SOFT_APPROVAL_TOKENS: set[str] = {
    "ja",
    "yes",
    "y",
    "ok",
    "okay",
    "speichern",
    "loeschen",
    "löschen",
    "write",
    "schreiben",
    "confirm",
    "bestätigen",
    "bestaetigen",
}

DEFAULT_EXCLUDED_PATH_PARTS: tuple[str, ...] = (
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
)


@dataclass(frozen=True)
class ApprovalTokenLiteral:
    """One string literal found in local Python source."""

    file_path: str
    line_number: int
    value: str


@dataclass(frozen=True)
class ApprovalTokenFinding:
    """One approval token scanner finding."""

    file_path: str | None
    line_number: int | None
    token_key: str | None
    token_value: str
    finding_type: ApprovalTokenFindingType
    message: str


@dataclass(frozen=True)
class ApprovalTokenScanResult:
    """Result of scanning local Python files for approval token regressions."""

    checked_files: tuple[str, ...]
    literals: tuple[ApprovalTokenLiteral, ...]
    findings: tuple[ApprovalTokenFinding, ...]
    passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def scan_python_source_for_string_literals(
    source: str,
    file_path: str = "<memory>",
) -> tuple[ApprovalTokenLiteral, ...]:
    """Collect string literals from Python source via AST."""
    tree = ast.parse(source, filename=file_path)
    literals: list[ApprovalTokenLiteral] = []
    # JSON/dict response keys such as {"ok": True} are data-shape labels, not
    # approval tokens. Keep values and every other literal in scope.
    structural_dict_key_ids = {
        id(key)
        for node in ast.walk(tree)
        if isinstance(node, ast.Dict)
        for key in node.keys
        if isinstance(key, ast.Constant) and key.value == "ok"
    }

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in structural_dict_key_ids
        ):
            literals.append(
                ApprovalTokenLiteral(
                    file_path=file_path,
                    line_number=node.lineno,
                    value=node.value,
                )
            )

    return tuple(literals)


def evaluate_approval_token_literals(
    literals: Iterable[ApprovalTokenLiteral],
    expected_tokens: dict[str, str] | None = None,
    soft_tokens: set[str] | None = None,
    allow_soft_token_values: set[str] | None = None,
) -> tuple[ApprovalTokenFinding, ...]:
    """Evaluate collected string literals for approval token regressions."""
    expected = expected_tokens or EXPECTED_APPROVAL_TOKENS
    soft = soft_tokens or SOFT_APPROVAL_TOKENS
    allowed_soft_values = allow_soft_token_values or set()
    expected_values = set(expected.values())

    literal_values = tuple(literal.value for literal in literals)
    findings: list[ApprovalTokenFinding] = []

    for token_key, token_value in expected.items():
        if token_value not in literal_values:
            findings.append(
                ApprovalTokenFinding(
                    file_path=None,
                    line_number=None,
                    token_key=token_key,
                    token_value=token_value,
                    finding_type="missing_expected_token",
                    message=(
                        f"Expected approval token {token_value!r} "
                        f"for {token_key} is missing."
                    ),
                )
            )

    allowed_soft_normalized = {value.strip().lower() for value in allowed_soft_values}

    for literal in literals:
        normalized = literal.value.strip().lower()
        if literal.value in expected_values:
            continue

        if normalized in soft and normalized not in allowed_soft_normalized:
            findings.append(
                ApprovalTokenFinding(
                    file_path=literal.file_path,
                    line_number=literal.line_number,
                    token_key=None,
                    token_value=literal.value,
                    finding_type="soft_token_detected",
                    message=f"Soft approval token {literal.value!r} detected.",
                )
            )

    return tuple(findings)


def scan_python_file_for_approval_tokens(
    file_path: str | Path,
) -> tuple[ApprovalTokenLiteral, ...]:
    """Scan one local Python file for approval token literals."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    return scan_python_source_for_string_literals(source, file_path=str(path))


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


def scan_paths_for_approval_token_regressions(
    roots: Iterable[str | Path],
    expected_tokens: dict[str, str] | None = None,
    soft_tokens: set[str] | None = None,
    allow_soft_token_values: set[str] | None = None,
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
) -> ApprovalTokenScanResult:
    """Scan paths for approval token regressions."""
    python_files = iter_python_files(roots, excluded_path_parts=excluded_path_parts)
    checked_files: list[str] = []
    literals: list[ApprovalTokenLiteral] = []

    for file_path in python_files:
        checked_files.append(str(file_path))
        literals.extend(scan_python_file_for_approval_tokens(file_path))

    findings = evaluate_approval_token_literals(
        literals,
        expected_tokens=expected_tokens,
        soft_tokens=soft_tokens,
        allow_soft_token_values=allow_soft_token_values,
    )

    return ApprovalTokenScanResult(
        checked_files=tuple(checked_files),
        literals=tuple(literals),
        findings=findings,
        passed=not findings,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
