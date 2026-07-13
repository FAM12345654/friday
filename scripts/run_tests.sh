#!/usr/bin/env bash
# Run the Friday test suites (cross-platform equivalent of run_tests.bat).
set -euo pipefail
cd "$(dirname "$0")/.."

if ! python3 -m pytest --version >/dev/null 2>&1; then
    echo "Pytest fehlt. Installiere Test-Requirements..."
    python3 -m pip install -r requirements-test.txt
fi

echo "Running Friday tests..."
python3 -m pytest friday/tests friday-api/tests "$@"
