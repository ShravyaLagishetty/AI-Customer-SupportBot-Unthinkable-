import sqlite3, os
from pathlib import Path

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./data/dev.db")
# support sqlite:///./path and fallback
if DB_PATH.startswith("sqlite:///"):
    sqlite_file = DB_PATH.replace("sqlite:///", "")
else:
    sqlite_file = "./data/dev.db"

def get_db():
    conn = sqlite3.connect(sqlite_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    Path("./data").mkdir(parents=True, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    # sessions, messages, faqs, escalations, feedback
    c.executescript("""CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        start_at TEXT,
        last_active_at TEXT,
        status TEXT
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        tags TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        reason TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        message_id INTEGER,
        rating INTEGER,
        comments TEXT,
        created_at TEXT
    );""")
    conn.commit()
    conn.close()
