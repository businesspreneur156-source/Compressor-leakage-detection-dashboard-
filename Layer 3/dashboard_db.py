"""Layer 3 - Streamlit dashboard (SQLite DB se data).

Run: streamlit run layer3/dashboard_db.py
Browser: http://localhost:8501

Layer 1 dashboard se farq: ye CSV nahi, database padhta hai,
isliye purana data, total readings aur leak count bhi dikhata hai.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from layer3.database import get_recent, get_stats  # noqa: E402

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Compressor Dashboard - Database", layout="wide")
st.title("Compressor Monitoring Dashboard - Database (Layer 3)")

stats = get_stats()
c1, c2, c3 = st.columns(3)
c1.metric("Total readings", stats["total"])
c2.metric("Possible Leakage", stats["leaks"])
c3.metric("Warning", stats["warnings"])

if st.button("Refresh"):
    st.rerun()

rows = get_recent(100)
if not rows:
    st.warning(
        "Database khaali hai. Pehle chalao: python layer3/database.py "
        "ya python layer3/import_csv_to_db.py (purani CSV se)"
    )
    st.stop()

df = pd.DataFrame(rows)
latest = df.iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pressure", f"{latest['pressure']} bar")
c2.metric("Temperature", f"{latest['temperature']} °C")
c3.metric("Airflow", f"{latest['flow']} L/min")
c4.metric("Leakage Status", str(latest["leakage"]))
if str(latest["leakage"]) == "Possible Leakage":
    st.error(f"⚠️ Possible Leakage! Reason: {latest.get('reason', '')}")
elif str(latest["leakage"]) == "Warning":
    st.warning(f"Check karo: {latest.get('reason', '')}")
else:
    st.success("✅ Normal")

status_filter = st.selectbox(
    "Filter", ["All", "Normal", "Warning", "Possible Leakage"]
)
show = df if status_filter == "All" else df[df["leakage"] == status_filter]
st.subheader("Pressure")
st.line_chart(show.set_index("timestamp")["pressure"])
st.subheader("Temperature")
st.line_chart(show.set_index("timestamp")["temperature"])
st.subheader("Airflow")
st.line_chart(show.set_index("timestamp")["flow"])
st.subheader("Readings")
st.dataframe(show.tail(50), use_container_width=True)
