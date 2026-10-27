"""Layer 5 - Login wala Streamlit dashboard.

Run: streamlit run layer5/dashboard_login.py
Browser: http://localhost:8501

Bina login ke koi data nahi dikhega - pehle login page aayega.
Login ke baad data Layer 3 ke SQLite DB se aata hai (warna CSV se).

Demo login (pehle apne users bana lo, ya demo use karo):
    admin  / admin123  (sab kuch: stats + download)
    viewer / viewer123 (sirf dekh sakta hai, download nahi)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from layer3.database import get_recent, get_stats  # noqa: E402
from layer5.auth import authenticate, load_users  # noqa: E402

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Compressor Dashboard - Login", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ---------- Login gate: login ke bina aage kuch nahi ----------
if st.session_state.user is None:
    st.title("🔐 Compressor Dashboard - Login")
    if not load_users():
        st.error(
            "Koi user nahi mila. Pehle chalao: python layer5/create_user.py "
            "ya users.json.example ko users.json me copy karo."
        )
        st.stop()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.user = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error("❌ Galat username ya password.")
    st.caption("Demo: admin / admin123 (full) | viewer / viewer123 (sirf dekhna)")
    st.stop()

# ---------- Logged-in dashboard ----------
role = st.session_state.role
user = st.session_state.user
st.title("Compressor Monitoring Dashboard")
st.caption(f"Logged in: {user} ({role})")
if st.button("Logout"):
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

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
        "ya python layer3/import_csv_to_db.py"
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

st.subheader("Pressure")
st.line_chart(df.set_index("timestamp")["pressure"])
st.subheader("Temperature")
st.line_chart(df.set_index("timestamp")["temperature"])
st.subheader("Airflow")
st.line_chart(df.set_index("timestamp")["flow"])
st.subheader("Recent readings")
st.dataframe(df.tail(50), use_container_width=True)

# Admin ko hi download milega - viewer sirf dekh sakta hai.
if role == "admin":
    st.download_button(
        "⬇️ Readings CSV download karo (admin only)",
        df.to_csv(index=False),
        file_name="compressor_readings.csv",
        mime="text/csv",
    )
else:
    st.info("Viewer role: download sirf admin ko milta hai.")
