import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- iOS/Glassmorphism CSS ---
st.markdown("""
    <style>
    .card { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(15px); border-radius: 20px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); border: 1px solid rgba(255, 255, 255, 0.18); height: 100%; }
    .stat-title { font-size: 0.7rem; color: #8e8e93; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
    .stat-val { font-size: 1.5rem; font-weight: 700; color: #1c1c1e; margin: 5px 0; }
    .stat-footer { font-size: 0.75rem; font-weight: 600; }
    .stApp { background: #f2f2f7; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, value, footer, delta_val=None, is_bad_if_positive=False):
    color = "green" if (delta_val <= 0 if not is_bad_if_positive else delta_val >= 0) else "red"
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
    
    # Calcs
    avg_cal, avg_steps = df['Cal'].mean(), df['Steps'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    c7, c30 = df.tail(7)['Cal'].mean(), df.tail(30)['Cal'].mean()
    
    # Weight
    start_w, end_w = df.iloc[0]['Weight'], df.iloc[-1]['Weight']
    total_loss = start_w - end_w
    loss_per_week = (total_loss / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    target_date = datetime.now() + timedelta(days=(end_w - 175) / (loss_per_week / 7))

    # --- Energy ---
    st.subheader("⚡ Calories")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_card("Avg Daily", f"{avg_cal:.0f}", "All Time")
    with c2: render_card("vs Maint", f"{avg_cal-2500:.0f}", "vs 2500", avg_cal-2500, True)
    with c3: render_card("vs Target", f"{avg_cal-1633:.0f}", "vs 1633", avg_cal-1633, True)
    with c4: render_card("7D Avg", f"{c7:.0f}", "Calories")
    with c5: render_card("30D Avg", f"{c30:.0f}", "Calories")

    # --- Steps ---
    st.subheader("🚀 Steps & Momentum")
    r1, r2, r3, r4, r5, r6 = st.columns(6)
    with r1: render_card("All Time Avg", f"{avg_steps:,.0f}", "vs 10k", avg_steps-10000)
    with r2: render_card("7D Avg", f"{s7:,.0f}", "vs Avg", s7-avg_steps)
    with r3: render_card("14D Avg", f"{s14:,.0f}", "vs Avg", s14-avg_steps)
    with r4: render_card("30D Avg", f"{s30:,.0f}", "vs Avg", s30-avg_steps)
    with r5: render_card("Req 14D", f"{(10000*14 - df.tail(14)['Steps'].sum())/14:,.0f}", "Steps/Day")
    with r6: render_card("Req 30D", f"{(10000*30 - df.tail(30)['Steps'].sum())/30:,.0f}", "Steps/Day")

    # --- Macros & Weight ---
    st.subheader("🎯 Macros & Progress")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: render_card("Protein", f"{df['Prot'].mean():.0f}%", "Avg")
    with m2: render_card("Net Carbs", f"{df['Carb'].mean():.0f}%", "Avg")
    with m3: render_card("Fat", f"{df['Fat'].mean():.0f}%", "Avg")
    with m4: render_card("Total Loss", f"{total_loss:.1f} lbs", f"{int(total_loss//14)}st {total_loss%14:.1f}lbs")
    with m5: render_card("Target Date", target_date.strftime('%d %b'), "Est.")
    with m6: render_card("Latest Change", f"{df.iloc[-2]['Weight'] - df.iloc[-1]['Weight']:.1f} lbs", "Last record")

    with st.expander("📂 Raw Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
