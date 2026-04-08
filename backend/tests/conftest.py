"""Pytest configuration for backend tests."""

import os
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ENABLE_SCHEDULER", "false")