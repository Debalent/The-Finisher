from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_generate_local():
    resp = client.post('/api/lyrics/generate', json={"genre":"pop","bpm":100,"mood":"happy","theme":"sun"})
    assert resp.status_code == 200
    data = resp.json()
    assert 'lyrics' in data
    assert 'timestamp' in data
