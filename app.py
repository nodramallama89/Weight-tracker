import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- Modern Dashboard Styling ---
st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    h3 { color: #333; font-weight: 600; font-size: 1.1rem; margin-bottom: 15px; }
    .stat-val { font-size: 2.5rem; font-weight: 700; color: #111; }
    .stat-label { font-size: 0.9rem; color: #666; }
    .stApp { background-color: #f4f7f6; }
    </style>
""", unsafe_allow_html=True)

# Helper to render a "Card"
def render_card(title, value, label, delta=None):
    delta_html = f"<div style='font-size: 0.8rem; color: {'green' if delta and float(delta) <= 0 else 'red'}'>{delta}</div>" if delta else ""
    st.markdown(f"""
        <div class='card'>
            <h3>{title}</h3>
            <div class='stat-val'>{value}</div>
            <div class='stat-label'>{label}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

# --- Load Data Logic ---
@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        rows = ws.get_all_values()[1:]
        clean = []
        for r in rows:
            if not r[0]: continue
            def to_n(v):
                try: return float(str(v).replace('%','').replace(',',''))
                except: return 0.0
            d = {"Date": pd.to_datetime(r[0], format='%d/%m/%Y'), "Cal": to_n(r[1]), "Weight": to_n(r[3]), "Steps": to_n(r[12])}
            if d["Steps"] > 0: clean.append(d)
        return pd.DataFrame(clean)
    except Exception as e:
        st.error(e)
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # Logic
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Layout - Row 1: Energy
    st.subheader("⚡ Energy Status")
    c1, c2, c3 = st.columns(3)
    with c1: render_card("Average Calories", f"{avg_cal:.0f}", "Lifetime Avg")
    with c2: render_card("vs Target (1633)", f"{avg_cal-1633:.0f}", "Delta", delta=f"{avg_cal-1633:.0f}")
    with c3: render_card("vs Maint (2500)", f"{avg_cal-2500:.0f}", "Delta", delta=f"{avg_cal-2500:.0f}")

    # Layout - Row 2: Momentum
    st.subheader("🚀 Momentum (Steps)")
    r1, r2, r3 = st.columns(3)
    with r1: render_card("7D Avg", f"{s7:,.0f}", "Target: 10,000")
    with r2: render_card("14D Avg", f"{s14:,.0f}", "Target: 10,000")
    with r3: render_card("30D Avg", f"{s30:,.0f}", "Target: 10,000")

    with st.expander("📂 View Raw Telemetry Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
