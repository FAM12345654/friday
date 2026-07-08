"""Preview scanner for network-like usage in JS, PowerShell, and package scripts."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Iterable


SCRIPT_NETWORK_PATTERNS: dict[str, tuple[str, ...]] = {
    "javascript": (
        "fetch(",
        "xmlhttprequest",
        "axios.",
        "websocket(",
        "eventsource(",
        "http://",
        "https://",
    ),
    "powershell": (
        "invoke-webrequest",
        "invoke-restmethod",
        "start-bitstransfer",
        "cloudflared",
        "curl ",
        "iwr ",
        "irm ",
        "npx eas",
        "http://",
        "https://",
    ),
    "batch": (
        "curl ",
        "powershell ",
        "invoke-webrequest",
        "cloudflared",
        "cloudflare",
        "npx eas",
        "eas-cli",
        "http://",
        "https://",
    ),
    "package_script": (
        "eas ",
        "eas:",
        "eas-cli",
        "npx eas",
        "expo publish",
        "expo export",
        "expo update",
        "cloudflared",
        "cloudflare",
        "curl ",
        "invoke-webrequest",
        "http://",
        "https://",
    ),
}

SCRIPT_FILE_SUFFIXES: tuple[str, ...] = (
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".ps1",
    ".psm1",
    ".psd1",
    ".bat",
    ".cmd",
)

DEFAULT_EXCLUDED_PATH_PARTS: tuple[str, ...] = (
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
    ".cache",
    "cache",
    "dist",
    "build",
)

DEFAULT_MAX_SCRIPT_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class ScriptNetworkFinding:
    """One network-like script finding."""

    file_path: str
    line_number: int
    surface: str
    matched_pattern: str
    snippet: str


@dataclass(frozen=True)
class ScriptNetworkScanResult:
    """Result of scanning script-like files without executing them."""

    checked_files: tuple[str, ...]
    findings: tuple[ScriptNetworkFinding, ...]
    passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class ScriptNetworkScannerReadinessGate:
    """Readiness status before widening script-network scanning."""

    gate_name: str
    status: str
    ready_for_bounded_preview: bool
    ready_for_standard_smoke: bool
    preview_only: bool
    local_only: bool
    executes_scripts: bool
    persists_results: bool
    external_lookup_used: bool
    root_boundary_required: bool
    root_boundary_configured: bool
    size_limit_bytes: int | None
    allowlist_required_for_smoke: bool
    allowlist_configured: bool
    blocked_reasons: tuple[str, ...]
    required_next_gate: str
    message: str


def _surface_for_path(path: Path) -> str | None:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if name == "package.json":
        return "package_json"
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        return "javascript"
    if suffix in {".ps1", ".psm1", ".psd1"}:
        return "powershell"
    if suffix in {".bat", ".cmd"}:
        return "batch"
    return None


def _line_findings(
    source: str,
    file_path: str,
    surface: str,
    patterns: tuple[str, ...],
) -> tuple[ScriptNetworkFinding, ...]:
    findings: list[ScriptNetworkFinding] = []

    for line_number, line in enumerate(source.splitlines(), start=1):
        normalized = line.lower()
        for pattern in patterns:
            if pattern in normalized:
                findings.append(
                    ScriptNetworkFinding(
                        file_path=file_path,
                        line_number=line_number,
                        surface=surface,
                        matched_pattern=pattern,
                        snippet=line.strip(),
                    )
                )

    return tuple(findings)


def scan_script_source_for_network_usage(
    source: str,
    file_path: str = "<memory>",
    surface: str = "javascript",
) -> tuple[ScriptNetworkFinding, ...]:
    """Scan JS/PowerShell-like source text for network patterns."""

    patterns = SCRIPT_NETWORK_PATTERNS.get(surface, ())
    return _line_findings(source, file_path, surface, patterns)


def scan_package_json_source_for_network_usage(
    source: str,
    file_path: str = "<memory>",
) -> tuple[ScriptNetworkFinding, ...]:
    """Scan package.json scripts for publish/network-like commands."""

    try:
        data = json.loads(source or "{}")
    except json.JSONDecodeError:
        return _line_findings(
            source,
            file_path,
            "package_json",
            SCRIPT_NETWORK_PATTERNS["package_script"],
        )

    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return ()

    findings: list[ScriptNetworkFinding] = []
    for index, script_name in enumerate(sorted(scripts), start=1):
        command = scripts[script_name]
        if not isinstance(command, str):
            continue
        normalized = command.lower()
        for pattern in SCRIPT_NETWORK_PATTERNS["package_script"]:
            if pattern in normalized:
                findings.append(
                    ScriptNetworkFinding(
                        file_path=file_path,
                        line_number=index,
                        surface="package_script",
                        matched_pattern=pattern,
                        snippet=f"{script_name}: {command}",
                    )
                )

    return tuple(findings)


def build_script_network_scanner_readiness_gate(
    project_root: str | Path | None = None,
    max_file_size_bytes: int | None = DEFAULT_MAX_SCRIPT_FILE_BYTES,
    standard_smoke_requested: bool = False,
    allowlist_configured: bool = False,
) -> ScriptNetworkScannerReadinessGate:
    """Build a side-effect-free readiness gate for script-network scanning."""

    blocked_reasons: list[str] = []
    root_boundary_configured = project_root is not None
    has_positive_size_limit = (
        max_file_size_bytes is not None and max_file_size_bytes > 0
    )

    if not root_boundary_configured:
        blocked_reasons.append("ROOT_BOUNDARY_NOT_CONFIGURED")
    if not has_positive_size_limit:
        blocked_reasons.append("SIZE_LIMIT_NOT_CONFIGURED")
    if standard_smoke_requested:
        blocked_reasons.append("SMOKE_INTEGRATION_BLOCKED")
        if not allowlist_configured:
            blocked_reasons.append("SMOKE_ALLOWLIST_NOT_CONFIGURED")

    ready_for_bounded_preview = root_boundary_configured and has_positive_size_limit
    status = (
        "preview_ready"
        if ready_for_bounded_preview and not blocked_reasons
        else "blocked"
    )

    return ScriptNetworkScannerReadinessGate(
        gate_name="script_network_scanner_readiness_gate",
        status=status,
        ready_for_bounded_preview=ready_for_bounded_preview,
        ready_for_standard_smoke=False,
        preview_only=True,
        local_only=True,
        executes_scripts=False,
        persists_results=False,
        external_lookup_used=False,
        root_boundary_required=True,
        root_boundary_configured=root_boundary_configured,
        size_limit_bytes=max_file_size_bytes,
        allowlist_required_for_smoke=True,
        allowlist_configured=allowlist_configured,
        blocked_reasons=tuple(blocked_reasons),
        required_next_gate="SCRIPT_NETWORK_SCANNER_STANDARD_SMOKE_GATE",
        message=(
            "Script Network Scanner bleibt preview-only; Standard-Smoke-"
            "Integration braucht ein separates Scope-/Allowlist-Gate."
        ),
    )


def _is_within_project_root(candidate: Path, project_root: str | Path | None) -> bool:
    if project_root is None:
        return True

    try:
        candidate_resolved = candidate.resolve()
        root_resolved = Path(project_root).resolve()
        return os.path.commonpath(
            (str(candidate_resolved), str(root_resolved))
        ) == str(root_resolved)
    except (OSError, ValueError):
        return False


def _is_within_size_limit(
    candidate: Path,
    max_file_size_bytes: int | None,
) -> bool:
    if max_file_size_bytes is None:
        return True

    try:
        return candidate.stat().st_size <= max_file_size_bytes
    except OSError:
        return False


def scan_script_file_for_network_usage(
    file_path: str | Path,
) -> tuple[ScriptNetworkFinding, ...]:
    """Scan one local script-like file without executing it."""

    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    surface = _surface_for_path(path)

    if surface == "package_json":
        return scan_package_json_source_for_network_usage(source, file_path=str(path))
    if surface is None:
        return ()
    return scan_script_source_for_network_usage(
        source,
        file_path=str(path),
        surface=surface,
    )


def iter_script_files(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
    project_root: str | Path | None = None,
    max_file_size_bytes: int | None = DEFAULT_MAX_SCRIPT_FILE_BYTES,
) -> tuple[Path, ...]:
    """Return JS/PowerShell/package files under root paths."""

    files: list[Path] = []

    for root in roots:
        root_path = Path(root)
        if root_path.is_file():
            candidate_files = (root_path,)
        elif root_path.is_dir():
            candidate_files = tuple(root_path.rglob("*"))
        else:
            candidate_files = ()

        for candidate in candidate_files:
            if not candidate.is_file():
                continue
            if any(part in candidate.parts for part in excluded_path_parts):
                continue
            if _surface_for_path(candidate) is None:
                continue
            if not _is_within_project_root(candidate, project_root):
                continue
            if not _is_within_size_limit(candidate, max_file_size_bytes):
                continue
            files.append(candidate)

    return tuple(sorted(set(files)))


def scan_paths_for_script_network_usage(
    roots: Iterable[str | Path],
    excluded_path_parts: tuple[str, ...] = DEFAULT_EXCLUDED_PATH_PARTS,
    project_root: str | Path | None = None,
    max_file_size_bytes: int | None = DEFAULT_MAX_SCRIPT_FILE_BYTES,
) -> ScriptNetworkScanResult:
    """Scan local script-like files for network patterns without execution."""

    script_files = iter_script_files(
        roots,
        excluded_path_parts=excluded_path_parts,
        project_root=project_root,
        max_file_size_bytes=max_file_size_bytes,
    )
    checked_files: list[str] = []
    findings: list[ScriptNetworkFinding] = []

    for file_path in script_files:
        checked_files.append(str(file_path))
        findings.extend(scan_script_file_for_network_usage(file_path))

    return ScriptNetworkScanResult(
        checked_files=tuple(checked_files),
        findings=tuple(findings),
        passed=not findings,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
