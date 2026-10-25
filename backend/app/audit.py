import json
import sqlite3
import time
from datetime import datetime, timezone

DB_PATH = "audit.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            username TEXT,
            role TEXT,
            query_redacted TEXT,
            outcome TEXT,
            block_reason TEXT,
            pii_found TEXT,
            output_flags TEXT,
            sources TEXT,
            latency_ms INTEGER
        )
    """)
    return conn


def log_request(username, role, result, latency_ms):
    # Outcome priority: blocked > flagged > not_found > answered
    if result.get("blocked"):
        outcome = "blocked_input"
    elif result.get("output_flags") and not all(
        f.startswith("pii_in_output") for f in result["output_flags"]
    ):
        outcome = "blocked_output"
    elif not result.get("sources"):
        outcome = "not_found"
    else:
        outcome = "answered"

    conn = _conn()
    with conn:
        conn.execute(
            "INSERT INTO audit_log (ts, username, role, query_redacted, outcome, "
            "block_reason, pii_found, output_flags, sources, latency_ms) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(),
                username,
                role,
                result.get("redacted_query", ""),
                outcome,
                result.get("block_reason"),
                json.dumps(result.get("pii_found", [])),
                json.dumps(result.get("output_flags", [])),
                json.dumps([s["source"] for s in result.get("sources", [])]),
                latency_ms,
            ),
        )
    conn.close()