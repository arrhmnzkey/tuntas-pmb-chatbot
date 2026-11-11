"""Riwayat percakapan di SQLite. Semua nilai lewat parameter ? (anti SQL injection)."""
import sqlite3
from contextlib import closing


class ChatHistory:
    def __init__(self, path):
        self.path = path
        with closing(self._conn()) as conn, conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    text TEXT NOT NULL,
                    intent TEXT,
                    score REAL,
                    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
                )"""
            )

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, session_id, sender, text, intent=None, score=None):
        with closing(self._conn()) as conn, conn:
            conn.execute(
                "INSERT INTO messages (session_id, sender, text, intent, score) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, sender, text, intent, score),
            )

    def get(self, session_id):
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT sender, text, intent, score FROM messages "
                "WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def clear(self, session_id):
        with closing(self._conn()) as conn, conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

    def stats(self):
        with closing(self._conn()) as conn:
            per_intent = conn.execute(
                "SELECT COALESCE(intent, '(tidak dikenali)') AS intent, COUNT(*) AS n "
                "FROM messages WHERE sender = 'user' GROUP BY intent ORDER BY n DESC"
            ).fetchall()
            ringkas = conn.execute(
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN intent IS NULL THEN 1 ELSE 0 END) AS gagal, "
                "COUNT(DISTINCT session_id) AS sesi "
                "FROM messages WHERE sender = 'user'"
            ).fetchone()
            tak_dikenali = conn.execute(
                "SELECT text, score, created_at FROM messages "
                "WHERE sender = 'user' AND intent IS NULL ORDER BY id DESC LIMIT 20"
            ).fetchall()
        total = ringkas["total"] or 0
        gagal = ringkas["gagal"] or 0
        return {
            "total": total,
            "dikenali_persen": round(100 * (total - gagal) / total, 1) if total else 0,
            "tidak_dikenali": gagal,
            "sesi": ringkas["sesi"] or 0,
            "per_intent": [dict(r) for r in per_intent],
            "daftar_tak_dikenali": [dict(r) for r in tak_dikenali],
        }