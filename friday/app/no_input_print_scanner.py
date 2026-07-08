"""Local no-input/print scanner.

The scanner reads Python files and checks direct CLI side-effect calls via AST.
It does not execute scanned files.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BLOCKED_CALL_NAMES: set[str] = {
    "input",
    "print",
    "builtins.input",
    "builtins.print",
}

DEFAULT_EXCLUDED_PATH_PARTS: tuple[str, ...] = (
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
)


@dataclass(frozen=True)
class InputPrintFinding:
    """One direct input/print finding."""

    file_path: str
    line_number: int
    call_name: str
    blocked_name: str


@dataclass(frozen=True)
class NoInputPrintScanResult:
    """Result of scanning one or more local Python files."""

    checked_files: tuple[str, ...]
    findings: tuple[InputPrintFinding, ...]
    passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _attribute_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = _attribute_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr

    return None


def _collect_builtin_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "builtins":
            for alias in node.names:
                if alias.name in {"input", "print"}:
                    local_name = alias.asname or alias.name
                    aliases[local_name] = f"builtins.{alias.name}"

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "builtins":
                    local_name = alias.asname or "builtins"
                    aliases[local_name] = "builtins"

    return aliases


def _resolve_call_name(call_name: str, aliases: dict[str, str]) -> str:
    parts = call_name.split(".")
    if not parts:
        return call_name

    root = parts[0]
    if root not in aliases:
        return call_name

    resolved_root = aliases[root]
    return ".".join((resolved_root, *parts[1:]))


def scan_python_source_for_input_print(
    source: str,
    file_path: str = "<memory>",
) -> tuple[InputPrintFinding, ...]:
    """Scan Python source text for direct input/print calls."""
    tree = ast.parse(source, filename=file_path)
    aliases = _collect_builtin_aliases(tree)
    findings: list[InputPrintFinding] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = _attribute_name(node.func)
        if not call_name:
            continue

        resolved_call_name = _resolve_call_name(call_name, aliases)

        if resolved_call_name in BLOCKED_CALL_NAMES:
            findings.append(
                InputPrintFinding(
                    file_path=file_path,
                    line_number=node.lineno,
                    call_name=resolved_call_name,
                    blocked_name=resolved_call_name,
                )
            )

    return tuple(findings)


def scan_python_file_for_input_print(
    file_path: str | Path,
) -> tuple[InputPrintFinding, ...]:
    """Scan one local Python file for direct input/print calls."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    return scan_python_source_for_input_print(source, file_path=str(path))


def iter_python_files(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
    excluded_file_paths: tuple[str | Path, ...] = (),
) -> tuple[Path, ...]:
    """Return Python files below root paths, skipping excluded paths."""
    files: list[Path] = []
    excluded_paths = {Path(path) for path in excluded_file_paths}

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
            if candidate in excluded_paths:
                continue
            files.append(candidate)

    return tuple(sorted(set(files)))


def scan_paths_for_input_print(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
    excluded_file_paths: tuple[str | Path, ...] = (),
) -> NoInputPrintScanResult:
    """Scan local Python files below the given roots for input/print calls."""
    python_files = iter_python_files(
        roots,
        excluded_path_parts=excluded_path_parts,
        excluded_file_paths=excluded_file_paths,
    )
    checked_files: list[str] = []
    findings: list[InputPrintFinding] = []

    for file_path in python_files:
        checked_files.append(str(file_path))
        findings.extend(scan_python_file_for_input_print(file_path))

    return NoInputPrintScanResult(
        checked_files=tuple(checked_files),
        findings=tuple(findings),
        passed=not findings,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
