"""Layer 1 - Synthetic sensor data + leakage detection logic.

Normal ranges (project ke defined rules):
    Pressure:    6.8 - 7.5 bar
    Temperature: 35 - 50 C
    Flow:        180 - 220 L/min

Leakage ke signs (yehi detection logic hai):
    1. Pressure 6.2 bar se neeche girna
    2. Pichhli reading se pressure me 0.8 bar se zyada sudden drop
    3. Flow 240 L/min se upar (compressor leak compensate karne ke liye zyada chal raha)
    4. Temperature 55 C se upar

Score: 3+ = Possible Leakage, 2 = Warning, 0-1 = Normal.
Leak tabhi declare hota hai jab ek se zyada signs ek saath milen -
sirf ek value hilne se false alarm nahi aayega. Yehi viva me samjhana hai.
"""
import random
import time
from datetime import datetime


def detect_leakage(pressure, temperature, flow, prev_pressure=None):
    """Return (status, reasons list). Status: Normal / Warning / Possible Leakage."""
    score = 0
    reasons = []
    if pressure < 6.2:
        score += 2
        reasons.append(f"Pressure low: {pressure} bar (< 6.2)")
    if prev_pressure is not None and (prev_pressure - pressure) > 0.8:
        score += 2
        reasons.append(f"Sudden pressure drop: {prev_pressure} -> {pressure} bar")
    if flow > 240:
        score += 1
        reasons.append(f"Flow high: {flow} L/min (> 240)")
    if temperature > 55:
        score += 1
        reasons.append(f"Temperature high: {temperature} C (> 55)")

    if score >= 3:
        return "Possible Leakage", reasons
    if score == 2:
        return "Warning", reasons
    return "Normal", reasons


def generate_reading(leak=False, prev_pressure=None):
    """One simulated reading. leak=True forces a leakage-like pattern."""
    if leak:
        pressure = round(random.uniform(5.0, 6.0), 2)
        temperature = round(random.uniform(55, 65), 1)
        flow = round(random.uniform(250, 300), 1)
    else:
        pressure = round(random.uniform(6.8, 7.5), 2)
        temperature = round(random.uniform(35, 50), 1)
        flow = round(random.uniform(180, 220), 1)
    status, reasons = detect_leakage(pressure, temperature, flow, prev_pressure)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pressure": pressure,
        "temperature": temperature,
        "flow": flow,
        "leakage": status,
        "reason": "; ".join(reasons),
    }


if __name__ == "__main__":
    # Demo: 5 normal + 3 leak readings, taaki logic aankhon se verify ho.
    prev = None
    print("--- Normal ---")
    for _ in range(5):
        r = generate_reading(leak=False, prev_pressure=prev)
        prev = r["pressure"]
        print(r)
        time.sleep(0.2)
    print("--- Leak injected ---")
    for _ in range(3):
        r = generate_reading(leak=True, prev_pressure=prev)
        prev = r["pressure"]
        print(r)
        time.sleep(0.2)
