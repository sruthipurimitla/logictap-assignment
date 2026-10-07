from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "calls.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            call_id TEXT PRIMARY KEY,
            status TEXT,
            duration_secs INTEGER
        )
    """)

    conn.commit()
    conn.close()


@app.route("/call-ended", methods=["POST"])
def call_ended():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    call_id = data.get("call_id")

    if not call_id:
        return jsonify({"error": "call_id is required"}), 400

    status = data.get("status")
    duration_secs = data.get("duration_secs")

    conn = get_db()

    existing = conn.execute(
        "SELECT call_id FROM calls WHERE call_id = ?",
        (call_id,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"message": "call already exists"}), 200

    conn.execute(
        """
        INSERT INTO calls (call_id, status, duration_secs)
        VALUES (?, ?, ?)
        """,
        (call_id, status, duration_secs)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "call stored successfully"}), 200


@app.route("/calls/<call_id>", methods=["GET"])
def get_call(call_id):
    conn = get_db()

    call = conn.execute(
        "SELECT call_id, status, duration_secs FROM calls WHERE call_id = ?",
        (call_id,)
    ).fetchone()

    conn.close()

    if not call:
        return jsonify({"error": "call not found"}), 404

    return jsonify(dict(call)), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)