from app import app, init_db
import os
import sqlite3


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

    # Send the same call twice
    first = client.post("/call-ended", json=data)
    second = client.post("/call-ended", json=data)

    # Both requests should succeed
    assert first.status_code == 200
    assert second.status_code == 200

    # Check that only ONE record exists in the database
    conn = sqlite3.connect("calls.db")
    count = conn.execute(
        "SELECT COUNT(*) FROM calls WHERE call_id = ?",
        ("test123",)
    ).fetchone()[0]
    conn.close()

    assert count == 1

    # Confirm the stored record can be retrieved
    result = client.get("/calls/test123")

    assert result.status_code == 200
    assert result.get_json()["call_id"] == "test123"