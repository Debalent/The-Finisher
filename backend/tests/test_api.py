import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_generate_default(client):
    resp = client.post('/api/lyrics/generate', json={})
    assert resp.status_code == 200
    data = resp.json()
    assert 'lyrics' in data
    assert 'timestamp' in data
