import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- CSS for Cards ---
st.markdown("""
    <style>
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .val { font-size: 24px; font-weight: bold; }
    .footer { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, value, footer, delta, is_good_if_higher):
    # Logic: If is_good_if_higher is True: Green if delta >= 0, Red if delta < 0
    # If False (Calories): Green if delta <= 0, Red if delta > 0
    if is_good_if_higher:
        color = "green" if delta >= 0 else "red"
        arrow = "↑" if delta >= 0 else "↓"
    else:
        color = "green" if delta <= 0 else "red"
        arrow = "↓" if delta <= 0 else "↑"
    
    st.markdown(f"""
        <div class='card'>
            <div style='color:grey; font-size:12px; text-transform:uppercase;'>{title}</div>
            <div class='val'>{value}</div>
            <div class='footer' style='color:{color}'>{arrow} {abs(delta):.0f} {footer}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Data Load ---
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
            d = {"Date": pd.to_datetime(r[0], format='%d/%m/%Y'), "Cal": to_n(r[1]), "Weight": to_n(r[3]), "Steps": to_n(r[12]), "Prot": to_n(r[16]), "Carb": to_n(r[17]), "Fat": to_n(r[18])}
            if d["Steps"] > 0: clean.append(d)
        return pd.DataFrame(clean)
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Weight Logic
    latest_change = df.iloc[-1]['Weight'] - df.iloc[-2]['Weight']
    
    # Energy Row
    st.subheader("⚡ Energy")
    c1, c2, c3 = st.columns(3)
    with c1: render_card("Avg Calories", f"{avg_cal:.0f}", "Lifetime Avg", 0, False)
    with c2: render_card("vs Target 1633", f"{avg_cal:.0f}", "vs Target", avg_cal-1633, False)
    with c3: render_card("vs Maint 2500", f"{avg_cal:.0f}", "vs Maint", avg_cal-2500, False)
    
    # Steps Row
    st.subheader("🚀 Steps")
    r1, r2, r3 = st.columns(3)
    with r1: render_card("7D Avg", f"{s7:,.0f}", "vs 10k", s7-10000, True)
    with r2: render_card("14D Req", f"{10000 - s14:,.0f}", "Steps/Day", 0, True) # Fixed projection
    with r3: render_card("Latest Change", f"{latest_change:.1f} lbs", "Gain/Loss", latest_change * -1, True)
