import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- Polished Styling ---
st.markdown("""
    <style>
    [data-testid="column"] { display: flex; }
    .card { background-color: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #eef0f2; flex-grow: 1; display: flex; flex-direction: column; }
    .stat-title { font-size: 0.75rem; color: #7f8c8d; text-transform: uppercase; font-weight: 600; }
    .stat-val { font-size: 1.8rem; font-weight: 700; color: #2c3e50; margin: 5px 0; }
    .stat-footer { font-size: 0.8rem; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, value, footer, delta_val=None, is_cal=False):
    # Logic: is_cal=True (lower is better), is_cal=False (higher is better)
    color = "green" if (delta_val <= 0 if is_cal else delta_val >= 0) else "red"
    arrow = "↑" if delta_val > 0 else "↓" if delta_val < 0 else ""
    st.markdown(f"""
        <div class='card'>
            <div class='stat-title'>{title}</div>
            <div class='stat-val'>{value}</div>
            <div class='stat-footer' style='color:{color}'>{arrow} {abs(delta_val):.0f} {footer}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Data Loading (Validated) ---
@st.cache_data(ttl=60)
def load_data():
    try:
        client = gspread.authorize(Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]))
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        rows = ws.get_all_values()[1:]
        clean = []
        for r in rows:
            if not r[0]: continue
            def to_n(v):
                try: return float(str(v).replace('%','').replace(',',''))
                except: return 0.0
            d = {"Date": pd.to_datetime(r[0], format='%d/%m/%Y'), "Cal": to_n(r[1]), "Weight": to_n(r[3]), "Steps": to_n(r[12]), "Prot": to_n(r[16]), "Carb": to_n(r[17]), "Fat": to_n(r[18])}
            if d["Steps"] > 0: clean.append(d)
        return pd.DataFrame(clean)
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # Metrics
    avg_cal, avg_p, avg_c, avg_f = df['Cal'].mean(), df['Prot'].mean(), df['Carb'].mean(), df['Fat'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Projections
    req_14 = (10000 * 14 - df.tail(14)['Steps'].sum()) / 14
    req_30 = (10000 * 30 - df.tail(30)['Steps'].sum()) / 30

    st.subheader("⚡ Energy & Macros")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_card("Avg Calories", f"{avg_cal:.0f}", "vs Target 1633", avg_cal-1633, is_cal=True)
    with c2: render_card("Protein", f"{avg_p:.0f}%", "Avg Intake")
    with c3: render_card("Carbs", f"{avg_c:.0f}%", "Avg Intake")
    with c4: render_card("Fat", f"{avg_f:.0f}%", "Avg Intake")
    
    st.subheader("🚀 Momentum & Targets")
    r1, r2, r3, r4 = st.columns(4)
    with r1: render_card("7D Avg Steps", f"{s7:,.0f}", "vs Target 10k", s7-10000)
    with r2: render_card("14D Projection", f"{req_14:,.0f}", "req. steps/day")
    with r3: render_card("30D Projection", f"{req_30:,.0f}", "req. steps/day")
    with r4: render_card("Days on Diet", f"{len(df)}", "Journey length")

    with st.expander("📂 View Raw Telemetry Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
