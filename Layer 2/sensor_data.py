"""Layer 2 - Cloud ke liye sensor-jaisa simulated data.

Layer 1 se farq: yehi data HiveMQ Cloud par jaata hai.
Logic wahi hai (synthetic_data.py), taaki dono layers ka
leakage status ek jaisa rahe - do alag logic rakhna bug hota.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "layer1"))
from synthetic_data import detect_leakage, generate_reading  # noqa: E402

__all__ = ["detect_leakage", "generate_reading"]


def get_sensor_data(leak=False, prev_pressure=None):
    """Publisher ke liye simple naam - andar wahi generate_reading hai."""
    return generate_reading(leak=leak, prev_pressure=prev_pressure)


if __name__ == "__main__":
    print(get_sensor_data())
    print(get_sensor_data(leak=True))
