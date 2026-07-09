"""Local AST-based forbidden import scanner.

This scanner reads Python source files and reports forbidden imports.
It does not import scanned files, execute scanned code, call networks, or write data.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "openai",
    "requests",
    "httpx",
    "twilio",
    "googleapiclient",
    "msgraph",
    "whatsapp",
    "smtplib",
    "imaplib",
    "poplib",
    "socket",
)

ALLOWED_FORBIDDEN_IMPORT_FILES: dict[str, tuple[str, ...]] = {
    "email_smtp_sender.py": ("smtplib",),
    "email_imap_reader.py": ("imaplib",),
}


@dataclass(frozen=True)
class ForbiddenImportFinding:
    """One forbidden import finding in a local Python file."""

    path: str
    module: str
    import_name: str
    line: int
    reason: str


@dataclass(frozen=True)
class ForbiddenImportScanResult:
    """Result of scanning one or more local Python files."""

    findings: tuple[ForbiddenImportFinding, ...]
    scanned_files: tuple[str, ...]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool

    @property
    def passed(self) -> bool:
        return not self.findings


def _import_root(name: str) -> str:
    return (name or "").split(".", 1)[0]


def _is_forbidden_import(name: str, forbidden_roots: Iterable[str]) -> bool:
    return _import_root(name) in set(forbidden_roots)


def _is_allowed_for_file(path: str, module_root: str) -> bool:
    return module_root in ALLOWED_FORBIDDEN_IMPORT_FILES.get(Path(path).name, ())


def scan_python_source_for_forbidden_imports(
    source: str,
    path: str = "<memory>",
    forbidden_roots: Iterable[str] = FORBIDDEN_IMPORT_ROOTS,
) -> ForbiddenImportScanResult:
    """Scan Python source text for forbidden imports without executing it."""
    forbidden_roots_tuple = tuple(forbidden_roots)
    findings: list[ForbiddenImportFinding] = []

    tree = ast.parse(source, filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_root = _import_root(alias.name)
                if _is_forbidden_import(alias.name, forbidden_roots_tuple) and not _is_allowed_for_file(path, module_root):
                    findings.append(
                        ForbiddenImportFinding(
                            path=path,
                            module=_import_root(alias.name),
                            import_name=alias.name,
                            line=node.lineno,
                            reason="Forbidden import detected.",
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            module_root = _import_root(module_name)
            if _is_forbidden_import(module_name, forbidden_roots_tuple) and not _is_allowed_for_file(path, module_root):
                findings.append(
                    ForbiddenImportFinding(
                        path=path,
                        module=_import_root(module_name),
                        import_name=module_name,
                        line=node.lineno,
                        reason="Forbidden import detected.",
                    )
                )

    return ForbiddenImportScanResult(
        findings=tuple(findings),
        scanned_files=(path,),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def scan_python_file_for_forbidden_imports(
    file_path: Path | str,
    forbidden_roots: Iterable[str] = FORBIDDEN_IMPORT_ROOTS,
) -> ForbiddenImportScanResult:
    """Scan one local Python file for forbidden imports."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    return scan_python_source_for_forbidden_imports(
        source=source,
        path=str(path),
        forbidden_roots=forbidden_roots,
    )


def iter_python_files(root: Path | str) -> tuple[Path, ...]:
    """Return Python files under a file or directory path."""
    path = Path(root)
    if path.is_file():
        return (path,) if path.suffix == ".py" else ()
    if not path.exists():
        return ()
    return tuple(sorted(path.rglob("*.py")))


def scan_python_paths_for_forbidden_imports(
    paths: Iterable[Path | str],
    forbidden_roots: Iterable[str] = FORBIDDEN_IMPORT_ROOTS,
) -> ForbiddenImportScanResult:
    """Scan local Python files under the given paths for forbidden imports."""
    all_findings: list[ForbiddenImportFinding] = []
    scanned_files: list[str] = []

    for path in paths:
        for python_file in iter_python_files(path):
            result = scan_python_file_for_forbidden_imports(
                python_file,
                forbidden_roots=forbidden_roots,
            )
            scanned_files.extend(result.scanned_files)
            all_findings.extend(result.findings)

    return ForbiddenImportScanResult(
        findings=tuple(all_findings),
        scanned_files=tuple(scanned_files),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
