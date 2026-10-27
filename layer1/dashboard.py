"""Layer 1 - Streamlit dashboard (CSV se data padhta hai).

Run:  streamlit run layer1/dashboard.py
      (project root se chalao, taaki data/compressor_data.csv mile)
Browser: http://localhost:8501
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_FILE  # noqa: E402

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Compressor Monitoring Dashboard", layout="wide")
st.title("Compressor Monitoring Dashboard")
st.caption("Layer 1 - Simulated data | Source: data/compressor_data.csv")

if st.button("Refresh"):
    st.rerun()

if not DATA_FILE.exists():
    st.warning(
        "Abhi koi data nahi hai. Pehle chalao: "
        "python layer1/save_csv.py  (ya Layer 2 subscriber)"
    )
    st.stop()

df = pd.read_csv(DATA_FILE)
if df.empty:
    st.warning("CSV khaali hai. Data generate karo, phir Refresh dabao.")
    st.stop()

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
    st.success("✅ Normal - koi leakage nahi")

st.subheader("Pressure")
st.line_chart(df.set_index("timestamp")["pressure"])
st.subheader("Temperature")
st.line_chart(df.set_index("timestamp")["temperature"])
st.subheader("Airflow")
st.line_chart(df.set_index("timestamp")["flow"])

st.subheader("Recent readings")
st.dataframe(df.tail(20), use_container_width=True)
