"""Wspólne przygotowanie testów."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    # raise_server_exceptions=False: testujemy odpowiedź HTTP z handlera błędów, a nie sam wyjątek.
    return TestClient(create_app(), raise_server_exceptions=False)
