import os
import libsql_experimental as libsql

# Turso connection
_connection = None


def get_connection():
    """Get or create Turso database connection"""
    global _connection
    if _connection is None:
        url = os.environ.get("TURSO_DATABASE_URL")
        token = os.environ.get("TURSO_AUTH_TOKEN")

        if not url or not token:
            raise RuntimeError("TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")

        _connection = libsql.connect(database=url, auth_token=token)
        _init_schema()

    return _connection


def _init_schema():
    """Initialize database schema if not exists"""
    conn = _connection
    conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            full_result TEXT,
            transcript TEXT,
            audio_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def save_result(timestamp: str, filename: str, result_text: str,
                transcript: str = "", audio_url: str = "") -> bool:
    """Save result to Turso database. Returns True on success."""
    try:
        conn = get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO qa_results
               (timestamp, filename, full_result, transcript, audio_url)
               VALUES (?, ?, ?, ?, ?)""",
            (timestamp, filename, result_text, transcript, audio_url)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] save_result: {e}")
        return False


def get_history() -> list:
    """Get all records from database"""
    try:
        conn = get_connection()
        cursor = conn.execute(
            """SELECT timestamp, filename, full_result, transcript, audio_url
               FROM qa_results ORDER BY created_at DESC LIMIT 100"""
        )
        rows = cursor.fetchall()
        return [
            {
                'Timestamp': row[0],
                'Filename': row[1],
                'Full Result': row[2],
                'Transcript': row[3],
                'Audio_URL': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"[ERROR] get_history: {e}")
        return []


def find_record_by_timestamp(timestamp: str) -> dict | None:
    """Find a specific record by timestamp"""
    try:
        conn = get_connection()
        cursor = conn.execute(
            """SELECT timestamp, filename, full_result, transcript, audio_url
               FROM qa_results WHERE timestamp = ?""",
            (timestamp,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'Timestamp': row[0],
                'Filename': row[1],
                'Full Result': row[2],
                'Transcript': row[3],
                'Audio_URL': row[4]
            }
        return None
    except Exception as e:
        print(f"[ERROR] find_record_by_timestamp: {e}")
        return None
