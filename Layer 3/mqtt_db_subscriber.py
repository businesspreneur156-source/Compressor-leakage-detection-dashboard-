"""Layer 3 - HiveMQ subscriber jo data seedha SQLite DB me save karta hai.

Layer 2 subscriber se farq: ye CSV ke bajay database me likhta hai,
taaki Layer 3 dashboard purana data bhi filter karke dikha sake.
Login/credentials ka kaam bilkul Layer 2 jaisa hai (8883 + TLS,
.env se username/password). Connection failed: 5 ka matlab yahan
bhi wahi hai: Not authorized - .env / permissions check karo.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (  # noqa: E402
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_PORT,
    HIVEMQ_USERNAME,
    MQTT_TOPIC,
    check_credentials,
)
from layer3.database import save_reading  # noqa: E402

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to HiveMQ Cloud. Subscribed:", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    elif rc == 5:
        print("❌ Connection failed: 5 = Not authorized. .env aur HiveMQ")
        print("   Access Management > MQTT Credentials check karo (README dekho).")
    else:
        print(f"❌ Connection failed: {rc}")


def on_message(client, userdata, msg):
    try:
        reading = json.loads(msg.payload.decode())
    except Exception as e:
        print("Bad message:", e)
        return
    save_reading(reading)
    print(
        f"Saved to DB: Pressure={reading['pressure']} bar, "
        f"Temp={reading['temperature']} C, Flow={reading['flow']} L/min, "
        f"Status={reading['leakage']}"
    )


def main():
    if mqtt is None:
        print("❌ paho-mqtt install nahi hai. Chalao: pip install paho-mqtt")
        raise SystemExit(1)
    ok, msg = check_credentials()
    if not ok:
        print("❌", msg)
        raise SystemExit(1)
    client = mqtt.Client(client_id="compressor-db-subscriber-vyom")
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
    print("Waiting for messages... (rokne ke liye Ctrl + C)")
    client.loop_forever()


if __name__ == "__main__":
    main()
