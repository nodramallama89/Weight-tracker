import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

st.set_page_config(page_title="Hardy House Command", layout="wide")

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
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean numeric columns (B:Cal, M:Steps, Q:Prot, R:Carb, S:Fat, T:Alc)
        for col_idx in [1, 12, 16, 17, 18, 19]:
            df.iloc[:, col_idx] = pd.to_numeric(df.iloc[:, col_idx].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce').fillna(0)
        
        # Filter: Only completed days (Steps > 0)
        df = df[df.iloc[:, 12] > 0]
        df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y')
        return df.sort_values('Date')
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

# --- Helpers ---
def delta_color(val, reverse=False):
    # If reverse=True (like calories), lower is better (Green). If False (like steps), higher is better (Green).
    if reverse: return "inverse" if val <= 0 else "normal"
    return "normal" if val >= 0 else "inverse"

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # Calc Variables
    avg_cal = df.iloc[:, 1].mean()
    avg_steps = df.iloc[:, 12].mean()
    avg_prot = df.iloc[:, 16].mean()
    avg_carb = df.iloc[:, 17].mean()
    avg_fat = df.iloc[:, 18].mean()
    alc_freq = len(df) / (df.iloc[:, 19] > 0).sum() if (df.iloc[:, 19] > 0).sum() > 0 else 0
    
    # --- Tab 1: Key Metrics ---
    st.subheader("Calorie & Step Targets")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Calories", f"{avg_cal:.0f}", f"{avg_cal - 1633:.0f} vs Target", delta_color=delta_color(avg_cal - 1633, reverse=True))
    c2.metric("Avg Steps", f"{avg_steps:,.0f}", f"{avg_steps - 10000:.0f} vs Target", delta_color=delta_color(avg_steps - 10000))
    c3.metric("Maintenance Var", f"{2500 - avg_cal:.0f} kcal gap")

    st.subheader("Macro & Lifestyle")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Protein", f"{avg_prot:.0f}%")
    m2.metric("Avg Carbs", f"{avg_carb:.0f}%")
    m3.metric("Avg Fat", f"{avg_fat:.0f}%")
    m4.metric("Alcohol", f"1 in {alc_freq:.1f} days")

    st.subheader("Rolling Averages (7/14/30 Day)")
    r1, r2, r3 = st.columns(3)
    r1.metric("Steps (7d)", f"{df.tail(7).iloc[:, 12].mean():,.0f}")
    r2.metric("Steps (14d)", f"{df.tail(14).iloc[:, 12].mean():,.0f}")
    r3.metric("Steps (30d)", f"{df.tail(30).iloc[:, 12].mean():,.0f}")

    # --- Tab 2: Projections ---
    st.markdown("---")
    st.subheader("Projections")
    
    # Calc remaining steps for 10k avg
    remaining_steps_14 = (10000 * 14) - df.tail(14).iloc[:, 12].sum()
    st.info(f"💡 To hit a 10,000 avg over the next 14 days, you need to average {(remaining_steps_14/14):,.0f} steps/day.")

    # Dataframe
    st.subheader("Raw Data View")
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)

else:
    st.info("Waiting for data...")
