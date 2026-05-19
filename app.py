import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- Glassmorphism UI Styling ---
st.markdown("""
    <style>
    .card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.3); }
    .title { font-size: 0.8rem; color: #8e8e93; text-transform: uppercase; }
    .val { font-size: 1.6rem; font-weight: bold; color: #1c1c1e; }
    .delta { font-size: 0.8rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, value, delta_text, delta_val, is_good_if_higher):
    # Logic: 
    # If is_good_if_higher: Green if delta >= 0, Red if delta < 0 (Arrow: Up if delta >= 0)
    # If !is_good_if_higher (Calories): Green if delta <= 0, Red if delta > 0 (Arrow: Down if delta <= 0)
    
    is_positive_delta = delta_val >= 0
    if is_good_if_higher:
        color = "green" if is_positive_delta else "red"
        arrow = "↑" if is_positive_delta else "↓"
    else:
        color = "green" if not is_positive_delta else "red"
        arrow = "↓" if not is_positive_delta else "↑"
    
    st.markdown(f"""
        <div class='card'>
            <div class='title'>{title}</div>
            <div class='val'>{value}</div>
            <div class='delta' style='color:{color}'>{arrow} {delta_text}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Data Loading ---
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
    
    # Metrics
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Weight
    latest_diff = df.iloc[-1]['Weight'] - df.iloc[-2]['Weight'] # Positive = Gain
    total_loss = df.iloc[0]['Weight'] - df.iloc[-1]['Weight']
    
    # --- UI ---
    st.subheader("⚡ Energy")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_card("Avg Calories", f"{avg_cal:.0f}", "All Time", 0, True)
    with c2: render_card("vs Maint", f"{avg_cal:.0f}", f"{avg_cal-2500:.0f} vs 2500", avg_cal-2500, False)
    with c3: render_card("vs Target", f"{avg_cal:.0f}", f"{avg_cal-1633:.0f} vs 1633", avg_cal-1633, False)
    with c4: render_card("7D Avg", f"{df.tail(7)['Cal'].mean():.0f}", "cals", 0, True)
    with c5: render_card("30D Avg", f"{df.tail(30)['Cal'].mean():.0f}", "cals", 0, True)

    st.subheader("🚀 Steps")
    r1, r2, r3, r4, r5, r6 = st.columns(6)
    with r1: render_card("All Time Avg", f"{df['Steps'].mean():,.0f}", "vs 10k", df['Steps'].mean()-10000, True)
    with r2: render_card("7D Avg", f"{s7:,.0f}", "vs Avg", s7-df['Steps'].mean(), True)
    with r3: render_card("14D Avg", f"{s14:,.0f}", "vs Avg", s14-df['Steps'].mean(), True)
    with r4: render_card("30D Avg", f"{s30:,.0f}", "vs Avg", s30-df['Steps'].mean(), True)
    with r5: render_card("Req 14D", f"{10000-s14:,.0f}", "Steps/Day", 0, True)
    with r6: render_card("Req 30D", f"{10000-s30:,.0f}", "Steps/Day", 0, True)

    st.subheader("🎯 Macros & Weight")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: render_card("Protein", f"{df['Prot'].mean():.0f}%", "Avg", 0, True)
    with m2: render_card("Net Carbs", f"{df['Carb'].mean():.0f}%", "Avg", 0, True)
    with m3: render_card("Fat", f"{df['Fat'].mean():.0f}%", "Avg", 0, True)
    with m4: render_card("Total Loss", f"{total_loss:.1f} lbs", f"{int(total_loss//14)}st {total_loss%14:.1f}lbs", 0, True)
    with m5: render_card("Latest Change", f"{abs(latest_diff):.1f} lbs", "Gain/Loss", latest_diff * -1, True)
    with m6: render_card("Days on Diet", f"{len(df)}", "Logged Days", 0, True)

    with st.expander("📂 View Raw Telemetry Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
