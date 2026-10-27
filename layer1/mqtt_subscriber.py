"""Layer 1 - Basic prototype subscriber (local).

Local broker se message aate hi terminal me print karta hai
aur data/compressor_data.csv me save karta hai.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from save_csv import save_reading  # noqa: E402

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "compressor/sensor"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to local broker. Subscribed:", TOPIC)
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed: {rc}")


def on_message(client, userdata, msg):
    try:
        reading = json.loads(msg.payload.decode())
    except Exception as e:
        print("Bad message:", e)
        return
    save_reading(reading)
    print(
        f"Received: Pressure={reading['pressure']} bar, "
        f"Temp={reading['temperature']} C, Flow={reading['flow']} L/min, "
        f"Status={reading['leakage']}"
    )


if __name__ == "__main__":
    client = mqtt.Client(client_id="layer1-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Local broker nahi mila: {e}")
        print("Pehle local broker chalao, ya seedha Layer 2 (HiveMQ) use karo.")
        raise SystemExit(1)
    client.loop_forever()
