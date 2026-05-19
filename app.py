import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Styling: Clean, iOS-inspired Glassmorphism
st.markdown("""
    <style>
    .card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.3); height: 100%; }
    .title { font-size: 0.7rem; color: #8e8e93; text-transform: uppercase; font-weight: 700; }
    .val { font-size: 1.4rem; font-weight: 800; color: #000; margin: 5px 0; }
    .delta { font-size: 0.75rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, val, delta_text, delta_val, is_good_if_higher):
    # Matches your sheet: Higher steps = Good (Green), Higher cals = Bad (Red)
    color = "green" if (delta_val >= 0 if is_good_if_higher else delta_val <= 0) else "red"
    arrow = "↑" if delta_val > 0 else "↓" if delta_val < 0 else ""
    st.markdown(f"""
        <div class='card'>
            <div class='title'>{title}</div>
            <div class='val'>{val}</div>
            <div class='delta' style='color:{color}'>{arrow} {delta_text}</div>
        </div>
    """, unsafe_allow_html=True)

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
            clean.append({"Date": pd.to_datetime(r[0], format='%d/%m/%Y'), "Cal": to_n(r[1]), "Weight": to_n(r[3]), "Steps": to_n(r[12]), "Prot": to_n(r[16]), "Carb": to_n(r[17]), "Fat": to_n(r[18])})
        return pd.DataFrame(clean)
    except: return pd.DataFrame()

df = load_data()
if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # Simple, direct calculations
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Weight change calculation
    latest_diff = df.iloc[-1]['Weight'] - df.iloc[-2]['Weight']
    
    # --- Energy ---
    st.subheader("⚡ Energy")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_card("Avg Cals", f"{avg_cal:.0f}", "All Time", 0, True)
    with c2: render_card("vs Maint", f"{avg_cal-2500:.0f}", "vs 2500", avg_cal-2500, False)
    with c3: render_card("vs Target", f"{avg_cal-1633:.0f}", "vs 1633", avg_cal-1633, False)
    with c4: render_card("7D Avg", f"{df.tail(7)['Cal'].mean():.0f}", "Cals", 0, True)

    # --- Steps ---
    st.subheader("🚀 Steps")
    r1, r2, r3, r4, r5 = st.columns(5)
    with r1: render_card("Avg Steps", f"{df['Steps'].mean():,.0f}", "vs 10k", df['Steps'].mean()-10000, True)
    with r2: render_card("7D Avg", f"{s7:,.0f}", "vs Avg", s7-df['Steps'].mean(), True)
    with r3: render_card("30D Avg", f"{s30:,.0f}", "vs Avg", s30-df['Steps'].mean(), True)
    with r4: render_card("Req 14D", f"{10000-s14:,.0f}", "Steps/Day", 10000-s14, True)
    with r5: render_card("Req 30D", f"{10000-s30:,.0f}", "Steps/Day", 10000-s30, True)

    # --- Macros/Weight ---
    st.subheader("🎯 Macros & Progress")
    m1, m2, m3, m4 = st.columns(4)
    with m1: render_card("Protein", f"{df['Prot'].mean():.0f}%", "Avg", 0, True)
    with m2: render_card("Net Carbs", f"{df['Carb'].mean():.0f}%", "Avg", 0, True)
    with m3: render_card("Fat", f"{df['Fat'].mean():.0f}%", "Avg", 0, True)
    with m4: render_card("Gain/Loss", f"{abs(latest_diff):.1f} lbs", "Latest Record", latest_diff * -1, True)

    with st.expander("📂 Raw Data"): st.dataframe(df.sort_values(by='Date', ascending=False))
