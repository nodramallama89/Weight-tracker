import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# App config
st.set_page_config(page_title="Hardy House Command", layout="wide")

# Custom CSS for high-performance cockpit look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetric"] { 
        background-color: #1c2526; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #334444;
        color: #e0e0e0;
    }
    h2 { color: #00ffcc !important; }
    </style>
""", unsafe_allow_html=True)

# --- Authentication & Data Loading ---
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

# Load data
df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # --- Calculations ---
    avg_cal = df['Cal'].mean()
    avg_steps = df['Steps'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Lifetime Weight Loss stats
    loss_per_week = ((df.iloc[0]['Weight'] - df.iloc[-1]['Weight']) / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    weight_to_target = df.iloc[-1]['Weight'] - 175
    days_to_target = weight_to_target / (loss_per_week / 7) if loss_per_week > 0 else 0
    target_date = datetime.now() + timedelta(days=days_to_target)

    # --- UI Layout ---
    with st.container():
        st.subheader("⚡ Energy Status")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Calories", f"{avg_cal:.0f}", f"{avg_cal - 1633:.0f} vs Target", delta_color="inverse")
        c2.metric("vs Maintenance", f"{2500 - avg_cal:.0f} kcal", "Gap to 2500")
        c3.metric("Step Count (Avg)", f"{avg_steps:,.0f}")
    
    with st.container():
        st.subheader("🚀 Momentum (Steps)")
        r1, r2, r3 = st.columns(3)
        r1.metric("7D Avg", f"{s7:,.0f}")
        r2.metric("14D Avg", f"{s14:,.0f}", f"{s7-s14:,.0f} vs 14D", delta_color="normal")
        r3.metric("30D Avg", f"{s30:,.0f}", f"{s7-s30:,.0f} vs 30D", delta_color="normal")
    
    with st.container():
        st.subheader("🎯 Mission Milestones")
        d1, d2, d3 = st.columns(3)
        d1.metric("Days on Diet", len(df))
        d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")
        d3.metric("Est. Target Date", target_date.strftime('%b %d, %Y') if loss_per_week > 0 else "N/A")

    with st.expander("See Raw Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("Waiting for data...")
