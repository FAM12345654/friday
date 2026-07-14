"""Local no-network scanner.

The scanner reads Python files and checks common network call patterns via AST.
It does not execute scanned files.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


NETWORK_CALL_PATTERNS: set[str] = {
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.patch",
    "requests.delete",
    "requests.request",
    "httpx.get",
    "httpx.post",
    "httpx.put",
    "httpx.patch",
    "httpx.delete",
    "httpx.request",
    "httpx.Client",
    "httpx.AsyncClient",
    "urllib.request.urlopen",
    "urllib.request.Request",
    "socket.socket",
    "socket.create_connection",
    "smtplib.SMTP_SSL",
    "smtplib.SMTP",
    "imaplib.IMAP4_SSL",
    "aiohttp.ClientSession",
    "websocket.WebSocket",
    "websockets.connect",
}

ALLOWED_LOCAL_NETWORK_FILES: tuple[str, ...] = (
    "local_ollama_runtime.py",
    "email_smtp_sender.py",
    "email_imap_reader.py",
    "imap_mail_reader.py",
    "imap_mail_writer.py",
    "calendar_provider_google.py",
    "calendar_provider_ics.py",
    "ms_mail_provider.py",
    "open_meteo_weather.py",
    "briefing_push.py",
)

DEFAULT_EXCLUDED_PATH_PARTS: tuple[str, ...] = (
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
)


@dataclass(frozen=True)
class NetworkUsageFinding:
    """One direct network usage finding."""

    file_path: str
    line_number: int
    call_name: str
    matched_pattern: str


@dataclass(frozen=True)
class NoNetworkScanResult:
    """Result of scanning one or more local Python files."""

    checked_files: tuple[str, ...]
    findings: tuple[NetworkUsageFinding, ...]
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


def _collect_import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".", 1)[0]
                aliases[local_name] = alias.name

        if isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for alias in node.names:
                local_name = alias.asname or alias.name
                full_name = f"{module_name}.{alias.name}" if module_name else alias.name
                aliases[local_name] = full_name

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


def scan_python_source_for_network_usage(
    source: str,
    file_path: str = "<memory>",
) -> tuple[NetworkUsageFinding, ...]:
    """Scan Python source text for known network call patterns."""
    tree = ast.parse(source, filename=file_path)
    aliases = _collect_import_aliases(tree)
    findings: list[NetworkUsageFinding] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = _attribute_name(node.func)
        if not call_name:
            continue

        resolved_call_name = _resolve_call_name(call_name, aliases)

        if resolved_call_name in NETWORK_CALL_PATTERNS and Path(file_path).name not in ALLOWED_LOCAL_NETWORK_FILES:
            findings.append(
                NetworkUsageFinding(
                    file_path=file_path,
                    line_number=node.lineno,
                    call_name=resolved_call_name,
                    matched_pattern=resolved_call_name,
                )
            )

    return tuple(findings)


def scan_python_file_for_network_usage(
    file_path: str | Path,
) -> tuple[NetworkUsageFinding, ...]:
    """Scan one local Python file for known network call patterns."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    return scan_python_source_for_network_usage(source, file_path=str(path))


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


def scan_paths_for_network_usage(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
) -> NoNetworkScanResult:
    """Scan local Python files below the given roots for network usage."""
    python_files = iter_python_files(roots, excluded_path_parts=excluded_path_parts)
    checked_files: list[str] = []
    findings: list[NetworkUsageFinding] = []

    for file_path in python_files:
        checked_files.append(str(file_path))
        findings.extend(scan_python_file_for_network_usage(file_path))

    return NoNetworkScanResult(
        checked_files=tuple(checked_files),
        findings=tuple(findings),
        passed=not findings,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
