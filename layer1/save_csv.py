"""Layer 1 - Readings ko CSV file me save karna.

CSV = table jaisi file, Excel/Sheets me khul jaati hai.
File: data/compressor_data.csv
Header sirf pehli baar likha jaata hai, uske baad rows append hoti hain.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_FILE  # noqa: E402

FIELDNAMES = ["timestamp", "pressure", "temperature", "flow", "leakage", "reason"]


def save_reading(reading):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    is_new = not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow({k: reading.get(k, "") for k in FIELDNAMES})
    return str(DATA_FILE)


if __name__ == "__main__":
    from synthetic_data import generate_reading

    for i in range(10):
        # Har 4th reading me leak inject karo, taaki CSV me dono status dikhen.
        reading = generate_reading(leak=(i % 4 == 3))
        print(save_reading(reading), reading)
    print("Done. 10 rows saved.")
