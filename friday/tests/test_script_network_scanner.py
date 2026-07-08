"""Tests for JS/PowerShell/package-script network scanner preview."""

from __future__ import annotations

from pathlib import Path

from friday.app.script_network_scanner import (
    DEFAULT_MAX_SCRIPT_FILE_BYTES,
    build_script_network_scanner_readiness_gate,
    iter_script_files,
    scan_package_json_source_for_network_usage,
    scan_paths_for_script_network_usage,
    scan_script_source_for_network_usage,
)


def _matched_patterns(findings) -> set[str]:
    return {finding.matched_pattern for finding in findings}


def test_script_network_scanner_allows_safe_javascript() -> None:
    findings = scan_script_source_for_network_usage(
        "const value = 1;\nconsole.log(value);\n",
        surface="javascript",
    )

    assert findings == ()


def test_script_network_scanner_detects_javascript_fetch() -> None:
    findings = scan_script_source_for_network_usage(
        "async function load() { return fetch('/api/tasks'); }\n",
        surface="javascript",
    )

    assert _matched_patterns(findings) == {"fetch("}
    assert findings[0].surface == "javascript"


def test_script_network_scanner_detects_powershell_downloads() -> None:
    findings = scan_script_source_for_network_usage(
        "Invoke-WebRequest https://example.test/file.zip\n",
        surface="powershell",
    )

    assert _matched_patterns(findings) == {"invoke-webrequest", "https://"}
    assert all(finding.surface == "powershell" for finding in findings)


def test_script_network_scanner_detects_package_publish_scripts() -> None:
    findings = scan_package_json_source_for_network_usage(
        """
        {
          "scripts": {
            "test": "node test.js",
            "publish": "npx eas-cli@latest update --branch preview"
          }
        }
        """
    )

    assert _matched_patterns(findings) == {"eas-cli", "npx eas"}
    assert findings[0].surface == "package_script"
    assert "publish:" in findings[0].snippet


def test_script_network_scanner_detects_batch_network_publish_commands() -> None:
    findings = scan_script_source_for_network_usage(
        "npx eas-cli update\r\ncloudflared tunnel --url http://localhost:8000\r\n",
        surface="batch",
    )

    assert {"eas-cli", "npx eas", "cloudflared", "http://"}.issubset(
        _matched_patterns(findings)
    )
    assert all(finding.surface == "batch" for finding in findings)


def test_scan_paths_for_script_network_usage_checks_supported_files(tmp_path) -> None:
    safe = tmp_path / "safe.js"
    blocked = tmp_path / "publish.ps1"
    package = tmp_path / "package.json"
    ignored = tmp_path / "notes.md"
    safe.write_text("const value = 1;\n", encoding="utf-8")
    blocked.write_text("cloudflared tunnel --url http://localhost:8000\n", encoding="utf-8")
    package.write_text(
        '{"scripts": {"build": "expo export --platform android"}}',
        encoding="utf-8",
    )
    ignored.write_text("https://example.test\n", encoding="utf-8")

    result = scan_paths_for_script_network_usage([tmp_path])

    assert len(result.checked_files) == 3
    assert result.passed is False
    assert {"cloudflared", "http://", "expo export"}.issubset(_matched_patterns(result.findings))
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_iter_script_files_skips_node_modules_and_cache(tmp_path) -> None:
    safe = tmp_path / "safe.js"
    node_modules = tmp_path / "node_modules"
    dot_cache = tmp_path / ".cache"
    cache_dir = tmp_path / "cache"
    cache = tmp_path / "__pycache__"
    blocked_node = node_modules / "blocked.js"
    blocked_dot_cache = dot_cache / "blocked.ps1"
    blocked_cache_dir = cache_dir / "blocked.cmd"
    blocked_cache = cache / "blocked.js"
    safe.write_text("const value = 1;\n", encoding="utf-8")
    node_modules.mkdir()
    dot_cache.mkdir()
    cache_dir.mkdir()
    cache.mkdir()
    blocked_node.write_text("fetch('https://example.test')\n", encoding="utf-8")
    blocked_dot_cache.write_text("Invoke-WebRequest https://example.test\n", encoding="utf-8")
    blocked_cache_dir.write_text("curl https://example.test\n", encoding="utf-8")
    blocked_cache.write_text("fetch('https://example.test')\n", encoding="utf-8")

    files = iter_script_files([tmp_path])

    assert files == (safe,)


def test_script_network_readiness_gate_requires_root_for_preview() -> None:
    gate = build_script_network_scanner_readiness_gate()

    assert gate.status == "blocked"
    assert gate.ready_for_bounded_preview is False
    assert gate.ready_for_standard_smoke is False
    assert gate.preview_only is True
    assert gate.local_only is True
    assert gate.executes_scripts is False
    assert "ROOT_BOUNDARY_NOT_CONFIGURED" in gate.blocked_reasons


def test_script_network_readiness_gate_blocks_standard_smoke_without_scope_gate(
    tmp_path,
) -> None:
    gate = build_script_network_scanner_readiness_gate(
        project_root=tmp_path,
        standard_smoke_requested=True,
    )

    assert gate.ready_for_bounded_preview is True
    assert gate.ready_for_standard_smoke is False
    assert "SMOKE_INTEGRATION_BLOCKED" in gate.blocked_reasons
    assert "SMOKE_ALLOWLIST_NOT_CONFIGURED" in gate.blocked_reasons
    assert gate.required_next_gate == "SCRIPT_NETWORK_SCANNER_STANDARD_SMOKE_GATE"


def test_script_network_readiness_gate_accepts_bounded_preview(tmp_path) -> None:
    gate = build_script_network_scanner_readiness_gate(project_root=tmp_path)

    assert gate.status == "preview_ready"
    assert gate.ready_for_bounded_preview is True
    assert gate.ready_for_standard_smoke is False
    assert gate.root_boundary_configured is True
    assert gate.size_limit_bytes == DEFAULT_MAX_SCRIPT_FILE_BYTES
    assert gate.blocked_reasons == ()


def test_scan_paths_for_script_network_usage_enforces_project_root(tmp_path) -> None:
    project_root = tmp_path / "project"
    outside_root = tmp_path / "outside"
    project_root.mkdir()
    outside_root.mkdir()
    inside = project_root / "safe.js"
    outside = outside_root / "blocked.js"
    inside.write_text("const value = 1;\n", encoding="utf-8")
    outside.write_text("fetch('https://example.test')\n", encoding="utf-8")

    result = scan_paths_for_script_network_usage(
        [tmp_path],
        project_root=project_root,
    )

    assert tuple(Path(path).name for path in result.checked_files) == ("safe.js",)
    assert result.findings == ()
    assert result.preview_only is True


def test_scan_paths_for_script_network_usage_skips_files_over_size_limit(
    tmp_path,
) -> None:
    large = tmp_path / "large.js"
    large.write_text("fetch('https://example.test')\n", encoding="utf-8")

    result = scan_paths_for_script_network_usage(
        [tmp_path],
        project_root=tmp_path,
        max_file_size_bytes=5,
    )

    assert result.checked_files == ()
    assert result.findings == ()
