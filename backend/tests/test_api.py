import pytest
from fastapi.testclient import TestClient

from backend.main import app
@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temp sqlite file for tests
    db_file = tmp_path / 'test.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_file}')
    from backend import db
    db.init_db()
    return TestClient(app)


def test_generate_default(client):
    resp = client.post('/api/lyrics/generate', json={})
    assert resp.status_code == 200
    data = resp.json()
    assert 'lyrics' in data
    assert 'timestamp' in data
    assert data.get('provider') in ('local', 'openai')
