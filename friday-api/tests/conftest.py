"""Test configuration for the friday-api test suite.

The API is a flat module layout (``perf.py``, ``main.py`` live directly in
``friday-api/``), so make that directory importable for the tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))
