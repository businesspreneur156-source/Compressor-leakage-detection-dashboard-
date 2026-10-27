"""Layer 1 - Basic prototype publisher (local, bina cloud ke).

Local test ke liye hai: agar laptop par koi local broker nahi hai,
to ye file sirf data print karegi - demo ke liye kaafi hai.
Cloud (HiveMQ) wala asli publisher layer2/mqtt_sensor_publisher.py hai.
"""
import json
import time

from synthetic_data import generate_reading

try:
    import paho.mqtt.client as mqtt

    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

BROKER = "localhost"
PORT = 1883
TOPIC = "compressor/sensor"


def main():
    prev = None
    client = None
    if HAS_MQTT:
        client = mqtt.Client(client_id="layer1-publisher")
        try:
            client.connect(BROKER, PORT, 60)
            client.loop_start()
            print(f"Connected to local broker {BROKER}:{PORT}")
        except Exception as e:
            print(f"Local broker nahi mila ({e}) - sirf print mode me chal raha hai.")
            client = None
    for i in range(20):
        reading = generate_reading(leak=(i % 5 == 4), prev_pressure=prev)
        prev = reading["pressure"]
        payload = json.dumps(reading)
        if client:
            client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(2)
    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
