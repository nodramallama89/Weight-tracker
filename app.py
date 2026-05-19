import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# CSS for Glassmorphism
st.markdown("""
    <style>
    .card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.3); height: 100%; }
    .title { font-size: 0.7rem; color: #8e8e93; text-transform: uppercase; font-weight: 700; }
    .val { font-size: 1.4rem; font-weight: 800; color: #1c1c1e; margin: 5px 0; }
    .delta { font-size: 0.75rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, val, delta_text, delta_val, is_good_if_higher):
    # Logic: Higher steps/lower calories = Green
    # Calories (is_good=False): Green if delta <= 0, Red if delta > 0
    # Steps/Weight Loss (is_good=True): Green if delta >= 0, Red if delta < 0
    if not is_good_if_higher: # Calories Logic
        color = "green" if delta_val <= 0 else "red"
        arrow = "↓" if delta_val <= 0 else "↑"
    else: # Steps/Progress Logic
        color = "green" if delta_val >= 0 else "red"
        arrow = "↑" if delta_val >= 0 else "↓"
    
    st.markdown(f"""
        <div class='card'>
            <div class='title'>{title}</div>
            <div class='val'>{val}</div>
            <div class='delta' style='color:{color}'>{arrow} {delta_text}</div>
        </div>
    """, unsafe_allow_html=True)

# Data Loading
@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        # Ensure we read the table fully
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        # Clean numeric cols
        cols = ['Cal', 'Weight', 'Steps', 'Prot', 'Carb', 'Fat']
        for c in cols: df[c] = pd.to_numeric(df[c].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        return df[df['Steps'] > 0]
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # Matching your spreadsheet logic (using sums/means of specific columns)
    # Average calories per day calculation (The Column average)
    avg_cal_per_day = df['Cal'].mean() 
    
    # Energy Row
    st.subheader("⚡ Energy")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_card("Avg Daily Cals", f"{avg_cal_per_day:.0f}", "", 0, True)
    with c2: render_card("vs Maint 2500", f"{avg_cal_per_day-2500:+.0f}", "vs 2500", avg_cal_per_day-2500, False)
    with c3: render_card("vs Target 1633", f"{avg_cal_per_day-1633:+.0f}", "vs 1633", avg_cal_per_day-1633, False)
    with c4: render_card("7D Avg Cals", f"{df.tail(7)['Cal'].mean():.0f}", "Cals", 0, True)

    # Steps Row
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    st.subheader("🚀 Steps")
    r1, r2, r3, r4, r5 = st.columns(5)
    with r1: render_card("Avg Steps", f"{df['Steps'].mean():,.0f}", f"{df['Steps'].mean()-10000:+.0f} vs 10k", df['Steps'].mean()-10000, True)
    with r2: render_card("7D Avg", f"{s7:,.0f}", f"{s7-df['Steps'].mean():+.0f} vs Avg", s7-df['Steps'].mean(), True)
    with r3: render_card("14D Avg", f"{s14:,.0f}", f"{s14-df['Steps'].mean():+.0f} vs Avg", s14-df['Steps'].mean(), True)
    with r4: render_card("Req 14D to 10k", f"{10000-s14:,.0f}", "Steps/Day", 0, True)
    with r5: render_card("Req 30D to 10k", f"{10000-s30:,.0f}", "Steps/Day", 0, True)

    # Macros Row
    st.subheader("🎯 Macros & Progress")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: render_card("Protein", f"{df['Prot'].mean():.0f}%", "Avg", 0, True)
    with m2: render_card("Carbs", f"{df['Carb'].mean():.0f}%", "Avg", 0, True)
    with m3: render_card("Fat", f"{df['Fat'].mean():.0f}%", "Avg", 0, True)
    loss = df.iloc[0]['Weight'] - df.iloc[-1]['Weight']
    with m4: render_card("Total Loss", f"{loss:.1f} lbs", f"{int(loss//14)}st {loss%14:.1f}lbs", loss, True)
    latest_gain = df.iloc[-1]['Weight'] - df.iloc[-2]['Weight']
    with m5: render_card("Latest Change", f"{abs(latest_gain):.1f} lbs", "Gain/Loss", latest_gain * -1, True)
