import pytest
from fastapi.testclient import TestClient

from core import queue_store
from main import app


@pytest.fixture
def client():
    queue_store.limpiar()
    return TestClient(app)
