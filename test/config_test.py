import os
import pytest
from fastapi.testclient import TestClient

# ensure sane defaults for tests without real .env
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_HOST", "127.0.0.1")
os.environ.setdefault("APP_PORT", "8000")
os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:1134")

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
