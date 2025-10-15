import os, sys, pytest
from fastapi.testclient import TestClient

# Ensure path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.main import app

client = TestClient(app)

def test_create_session_and_message_flow():
    # create session
    r = client.post('/api/v1/sessions')
    assert r.status_code == 200
    sid = r.json().get('session_id')
    assert sid
    # send message
    r2 = client.post(f'/api/v1/sessions/{sid}/message', json={'text':'Hello, my order is not arrived'})
    assert r2.status_code == 200
    j = r2.json()
    assert 'text' in j
    # list messages
    r3 = client.get(f'/api/v1/sessions/{sid}/messages')
    assert r3.status_code == 200
    msgs = r3.json()
    assert len(msgs) >= 1
