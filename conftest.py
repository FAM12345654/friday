"""Repository-wide pytest isolation for persistent security ledgers."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_persistent_security_ledgers(tmp_path, monkeypatch):
    """Never let tests read or mutate production approval/OAuth transactions."""

    monkeypatch.setenv(
        "FRIDAY_SECURITY_LEDGER_DB_PATH",
        str(tmp_path / "friday-security-ledger.db"),
    )
    monkeypatch.setenv(
        "FRIDAY_OAUTH_LEDGER_SECRET",
        "pytest-only-oauth-ledger-secret-32-characters",
    )
