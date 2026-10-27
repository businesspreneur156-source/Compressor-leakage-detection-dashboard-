"""Layer 3 - Purani CSV ko SQLite DB me daalo (ek baar ka migration).

Run: python layer3/import_csv_to_db.py
Pehle se DB me maujood timestamp+pressure wali rows dobara nahi dalta.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_FILE  # noqa: E402
from layer3.database import get_connection, init_db  # noqa: E402


def main():
    if not DATA_FILE.exists():
        print(f"CSV nahi mili: {DATA_FILE}")
        print("Pehle chalao: python run_demo.py")
        raise SystemExit(1)
    init_db()
    added = skipped = 0
    with open(DATA_FILE, newline="", encoding="utf-8") as f, get_connection() as conn:
        for row in csv.DictReader(f):
            exists = conn.execute(
                "SELECT 1 FROM readings WHERE timestamp = ? AND pressure = ?",
                (row["timestamp"], row["pressure"]),
            ).fetchone()
            if exists:
                skipped += 1
                continue
            conn.execute(
                "INSERT INTO readings (timestamp, pressure, temperature, flow, leakage, reason)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    row["timestamp"],
                    row["pressure"],
                    row["temperature"],
                    row["flow"],
                    row["leakage"],
                    row.get("reason", ""),
                ),
            )
            added += 1
    print(f"Done. Added: {added}, already present (skipped): {skipped}")


if __name__ == "__main__":
    main()
