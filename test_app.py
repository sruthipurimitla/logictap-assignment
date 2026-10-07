from app import app, init_db
import os


def test_duplicate_call_id_is_not_stored_twice():
    if os.path.exists("calls.db"):
        os.remove("calls.db")

    init_db()

    client = app.test_client()

    data = {
        "call_id": "test123",
        "status": "answered",
        "duration_secs": 42
    }

    first = client.post("/call-ended", json=data)
    second = client.post("/call-ended", json=data)

    assert first.status_code == 200
    assert second.status_code == 200

    result = client.get("/calls/test123")

    assert result.status_code == 200
    assert result.get_json()["call_id"] == "test123"