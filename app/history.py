import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "audit.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            username TEXT,
            role TEXT,
            query TEXT,
            answer TEXT,
            sources TEXT
        )
    """)
    return conn


def save(username, role, query, answer, sources):
    conn = _conn()
    with conn:
        # keep one entry per identical question
        conn.execute(
            "DELETE FROM chat_history WHERE username=? AND role=? AND query=?",
            (username, role, query),
        )
        conn.execute(
            "INSERT INTO chat_history (ts, username, role, query, answer, sources) "
            "VALUES (?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), username, role, query, answer,
             json.dumps(sources)),
        )
    conn.close()


def search(username, role, q="", limit=50):
    conn = _conn()
    sql = ("SELECT id, ts, query, answer, sources FROM chat_history "
           "WHERE username=? AND role=?")
    params = [username, role]
    if q.strip():
        sql += " AND query LIKE ?"
        params.append(f"%{q.strip()}%")
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [{"id": r[0], "ts": r[1], "query": r[2], "answer": r[3],
             "sources": json.loads(r[4])} for r in rows]


def delete(username, item_id):
    conn = _conn()
    with conn:
        conn.execute("DELETE FROM chat_history WHERE id=? AND username=?",
                     (item_id, username))
    conn.close()


def clear(username):
    conn = _conn()
    with conn:
        conn.execute("DELETE FROM chat_history WHERE username=?", (username,))
    conn.close()