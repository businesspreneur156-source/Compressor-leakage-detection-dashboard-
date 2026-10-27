"""Layer 2 - HiveMQ Cloud publisher (FIXED version).

Pehli wali problem ka asli kaaran aksar ye hota hai:
  * port 1883 (bina TLS) use karna, jabki HiveMQ Cloud ko 8883 + TLS chahiye
  * cluster admin password ko MQTT username/password samajhna
  * username_pw_set() connect() se PEHLE na lagana

Is file me teeno theek hain:
  * port 8883 + client.tls_set()
  * username_pw_set() connect se pehle
  * alag client_id (subscriber se takraav nahi)

Run:  python layer2/mqtt_sensor_publisher.py
Roko:  Ctrl + C
"""
import json
import sys
import time
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
from layer2.sensor_data import get_sensor_data  # noqa: E402

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None  # main() me saaf message milega, traceback nahi


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to HiveMQ Cloud. Publishing to:", MQTT_TOPIC)
    elif rc == 5:
        print("❌ Connection failed: 5 = Not authorized.")
        print("   -> Username/password galat hai, ya us credential ko")
        print("      is topic par Publish ki permission nahi hai.")
        print("   -> HiveMQ console > Access Management > MQTT Credentials me check karo.")
    else:
        print(f"❌ Connection failed: {rc}")


def main():
    if mqtt is None:
        print("❌ paho-mqtt install nahi hai. Chalao: pip install paho-mqtt")
        raise SystemExit(1)
    ok, msg = check_credentials()
    if not ok:
        print("❌", msg)
        print("   .env.example ko .env me copy karo aur asli values bharo.")
        raise SystemExit(1)

    client = mqtt.Client(client_id="compressor-publisher-vyom")
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.tls_set()  # HiveMQ Cloud ke liye zaroori
    client.on_connect = on_connect
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
    client.loop_start()

    prev = None
    try:
        i = 0
        while True:
            # Har 5th reading me leak, taaki dashboard par status badalta dikhe.
            reading = get_sensor_data(leak=(i % 5 == 4), prev_pressure=prev)
            prev = reading["pressure"]
            client.publish(MQTT_TOPIC, json.dumps(reading))
            print(f"Published: {reading}")
            i += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
