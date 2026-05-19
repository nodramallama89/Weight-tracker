import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# Corrected configuration
st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- High Contrast Cockpit CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    h2 { color: #00ffcc !important; border-bottom: 1px solid #334444; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- Data Loading (The "God Mode" logic) ---
def get_gsheets_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_data():
    try:
        client = get_gsheets_client()
        worksheet = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        rows = worksheet.get_all_values()[1:]
        clean_rows = []
        for r in rows:
            if not r[0]: continue
            def to_num(val):
                try: return float(str(val).replace('%','').replace(',',''))
                except: return 0.0
            row_data = {
                "Date": pd.to_datetime(r[0], format='%d/%m/%Y'),
                "Cal": to_num(r[1]),
                "Weight": to_num(r[3]),
                "Steps": to_num(r[12]),
                "Prot": to_num(r[16]),
                "Carb": to_num(r[17]),
                "Fat": to_num(r[18]),
                "Alc": to_num(r[19])
            }
            if row_data["Steps"] > 0: clean_rows.append(row_data)
        return pd.DataFrame(clean_rows)
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

# --- Main App ---
df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # Calculations
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # --- Energy Section ---
    st.subheader("⚡ Energy Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Calories", f"{avg_cal:.0f}")
    c2.metric("vs Target (1633)", f"{avg_cal - 1633:.0f}", delta_color="inverse")
    c3.metric("vs Maint (2500)", f"{avg_cal - 2500:.0f}", delta_color="inverse")
    
    # --- Momentum Section ---
    st.subheader("🚀 Momentum (Steps vs 10k Target)")
    r1, r2, r3 = st.columns(3)
    # Using 'normal' delta color so that higher than target shows Green
    r1.metric("7D Avg (vs 10k)", f"{s7:,.0f}", f"{s7 - 10000:,.0f}")
    r2.metric("14D Avg (vs 10k)", f"{s14:,.0f}", f"{s14 - 10000:,.0f}")
    r3.metric("30D Avg (vs 10k)", f"{s30:,.0f}", f"{s30 - 10000:,.0f}")
    
    # --- Milestones Section ---
    st.subheader("🎯 Mission Milestones")
    d1, d2, d3 = st.columns(3)
    d1.metric("Days on Diet", len(df))
    loss_per_week = ((df.iloc[0]['Weight'] - df.iloc[-1]['Weight']) / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")
    days_to_target = (df.iloc[-1]['Weight'] - 175) / (loss_per_week / 7) if loss_per_week > 0 else 0
    target_date = datetime.now() + timedelta(days=days_to_target)
    d3.metric("Est. Target Date", target_date.strftime('%b %d, %Y') if loss_per_week > 0 else "N/A")
else:
    st.info("Waiting for data...")
