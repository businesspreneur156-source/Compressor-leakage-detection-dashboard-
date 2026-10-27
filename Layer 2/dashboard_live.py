"""Layer 2 - Live dashboard (seedha HiveMQ se data leta hai, CSV ka wait nahi).

Run:  streamlit run layer2/dashboard_live.py
Browser: http://localhost:8501

Kaam karne ka tareeka:
  * Ek background thread MQTT subscriber chalata hai.
  * Aane wali har reading session_state me save hoti hai (aakhri 100).
  * Dashboard har 2 second me khud refresh hota hai (fragment).
  * Agar HiveMQ credentials nahi mile, to dashboard simulation mode me
    chalega - taaki demo kabhi khaali screen par na atke.
"""
import json
import queue
import sys
import threading
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

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Compressor Live Dashboard", layout="wide")
st.title("Compressor Monitoring Dashboard - LIVE")
st.caption("Layer 2 - HiveMQ Cloud se live data (na mile to simulation mode)")

if "readings" not in st.session_state:
    st.session_state.readings = []
if "mqtt_started" not in st.session_state:
    st.session_state.mqtt_started = False

msg_queue = queue.Queue()
ok, cred_msg = check_credentials()


def _mqtt_thread():
    import paho.mqtt.client as mqtt

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe(MQTT_TOPIC)

    def on_message(client, userdata, msg):
        try:
            msg_queue.put(json.loads(msg.payload.decode()))
        except Exception:
            pass

    client = mqtt.Client(client_id="compressor-dashboard-vyom")
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
    client.loop_forever()


def _simulation_thread():
    prev = None
    i = 0
    while True:
        reading = get_sensor_data(leak=(i % 5 == 4), prev_pressure=prev)
        prev = reading["pressure"]
        msg_queue.put(reading)
        i += 1
        time.sleep(2)


if not st.session_state.mqtt_started:
    target = _mqtt_thread if ok else _simulation_thread
    threading.Thread(target=target, daemon=True).start()
    st.session_state.mqtt_started = True
    if not ok:
        st.info(f"Simulation mode: {cred_msg} .env bharne par yehi dashboard live ho jayega.")

# Queue se nayi readings nikalo
while not msg_queue.empty():
    st.session_state.readings.append(msg_queue.get())
    st.session_state.readings = st.session_state.readings[-100:]


@st.fragment(run_every="2s")
def show_live():
    readings = st.session_state.readings
    if not readings:
        st.warning("Data ka wait ho raha hai... 2 second me aana chahiye.")
        return
    df = pd.DataFrame(readings)
    latest = df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pressure", f"{latest['pressure']} bar")
    c2.metric("Temperature", f"{latest['temperature']} °C")
    c3.metric("Airflow", f"{latest['flow']} L/min")
    status = str(latest["leakage"])
    c4.metric("Leakage Status", status)
    if status == "Possible Leakage":
        st.error(f"⚠️ Possible Leakage! Reason: {latest.get('reason', '')}")
    elif status == "Warning":
        st.warning(f"Check karo: {latest.get('reason', '')}")
    else:
        st.success("✅ Normal")
    st.subheader("Pressure")
    st.line_chart(df.set_index("timestamp")["pressure"])
    st.subheader("Temperature")
    st.line_chart(df.set_index("timestamp")["temperature"])
    st.subheader("Airflow")
    st.line_chart(df.set_index("timestamp")["flow"])
    st.subheader("Recent readings")
    st.dataframe(df.tail(20), use_container_width=True)


show_live()
