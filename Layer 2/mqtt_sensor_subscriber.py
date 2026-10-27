"""Layer 2 - HiveMQ Cloud subscriber (YEHI WALI FILE FIX HUI HAI).

Pehle error: "Connection failed: 5"
MQTT me rc=5 ka matlab sirf ek hai: Not authorized.
Ye network ya code ka error NAHI hai - login reject hua hai.

Fix checklist (is file ke saath README me bhi hai):
  1. Host sahi ho: HiveMQ console se copy kiya hua, jaise
     xxxxx.s1.eu.hivemq.cloud (keenbee cluster ka Overview page).
  2. Username/password HiveMQ console > Access Management >
     MQTT Credentials wale hon - cluster login password NAHI.
  3. Us credential ki Permissions me Publish + Subscribe dono hon,
     topic "compressor/sensor" par (ya "*" par).
  4. Port 8883 + TLS on ho (is file me hai).
  5. Publisher aur subscriber ka client_id ALAG ho (is file me hai).
  6. Cluster Running state me ho (Paused cluster bhi 5 de sakta hai).

Ye subscriber message milte hi:
  * terminal me print karta hai
  * data/compressor_data.csv me save karta hai
  * isliye Layer 1 dashboard bhi live data dikhane lagta hai.
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
from layer1.save_csv import save_reading  # noqa: E402

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None  # main() me saaf message milega, traceback nahi


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to HiveMQ Cloud. Subscribed:", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    elif rc == 5:
        print("❌ Connection failed: 5 = Not authorized.")
        print("   1) .env me username/password dobara check karo (koi space to nahi).")
        print("   2) HiveMQ console > Access Management me us user ki permission")
        print("      dekho: Subscribe allowed hai? Topic compressor/sensor hai?")
        print("   3) Cluster 'keenbee' Running hai ya Paused?")
        print("   Code me kuch aur badalne ki zaroorat nahi - login hi reject hua hai.")
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
        f"Received: Pressure={reading['pressure']} bar, "
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
        print("   .env.example ko .env me copy karo aur asli values bharo.")
        raise SystemExit(1)

    client = mqtt.Client(client_id="compressor-subscriber-vyom")
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
    print("Waiting for messages... (rokne ke liye Ctrl + C)")
    client.loop_forever()


if __name__ == "__main__":
    main()
