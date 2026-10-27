"""Layer 3 - SQLite database.

CSV me purana data dhoondhna mushkil hota hai; database me hum
date/status ke hisaab se filter kar sakte hain. SQLite ke liye
koi alag server install nahi karna padta - ye Python ke saath
hi aata hai, aur data ek file me save hota hai: data/compressor.db

Table: readings
    timestamp TEXT, pressure REAL, temperature REAL,
    flow REAL, leakage TEXT, reason TEXT
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR  # noqa: E402

DB_FILE = DATA_DIR / "compressor.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pressure REAL,
                temperature REAL,
                flow REAL,
                leakage TEXT,
                reason TEXT
            )
            """
        )
    return str(DB_FILE)


def save_reading(reading):
    init_db()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO readings (timestamp, pressure, temperature, flow, leakage, reason)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                reading.get("timestamp"),
                reading.get("pressure"),
                reading.get("temperature"),
                reading.get("flow"),
                reading.get("leakage"),
                reading.get("reason", ""),
            ),
        )
    return str(DB_FILE)


def get_recent(limit=100):
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def get_stats():
    init_db()
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        leaks = conn.execute(
            "SELECT COUNT(*) FROM readings WHERE leakage = 'Possible Leakage'"
        ).fetchone()[0]
        warnings = conn.execute(
            "SELECT COUNT(*) FROM readings WHERE leakage = 'Warning'"
        ).fetchone()[0]
    return {"total": total, "leaks": leaks, "warnings": warnings}


if __name__ == "__main__":
    print("DB:", init_db())
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "layer1"))
    from synthetic_data import generate_reading

    for i in range(5):
        r = generate_reading(leak=(i == 4))
        save_reading(r)
        print("Saved:", r)
    print("Stats:", get_stats())
    print("Recent:", len(get_recent()))
