import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

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

df = load_data()

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # --- Calculations ---
    # Global Averages (Diet History)
    avg_cal = df['Cal'].mean()
    avg_steps = df['Steps'].mean()
    avg_prot = df['Prot'].mean()
    avg_carb = df['Carb'].mean()
    avg_fat = df['Fat'].mean()
    alc_days = (df['Alc'] > 0).sum()
    alc_freq = len(df) / alc_days if alc_days > 0 else len(df)
    
    # Steps Windows
    s7 = df.tail(7)['Steps'].mean()
    s14 = df.tail(14)['Steps'].mean()
    s30 = df.tail(30)['Steps'].mean()
    
    # --- Layout ---
    st.subheader("Calorie & Step Targets (Journey Averages)")
    c1, c2, c3 = st.columns(3)
    # Calories: Over 1633 is RED (bad)
    c1.metric("Avg Calories", f"{avg_cal:.0f}", f"{avg_cal - 1633:.0f}", delta_color="inverse")
    c2.metric("Avg Steps (All time)", f"{avg_steps:,.0f}")
    c3.metric("Maintenance Var", f"{2500 - avg_cal:.0f} kcal gap", delta_color="normal")
    
    st.subheader("Rolling Step Trends")
    r1, r2, r3 = st.columns(3)
    r1.metric("7D Avg Steps", f"{s7:,.0f}")
    r2.metric("14D Avg Steps", f"{s14:,.0f}", f"{s7-s14:,.0f} vs 14D")
    r3.metric("30D Avg Steps", f"{s30:,.0f}", f"{s7-s30:,.0f} vs 30D")
    
    st.subheader("Lifestyle & Macros")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Protein", f"{avg_prot:.0f}%")
    m2.metric("Avg Carbs", f"{avg_carb:.0f}%")
    m3.metric("Avg Fat", f"{avg_fat:.0f}%")
    m4.metric("Alc Frequency", f"1 in {alc_freq:.1f} days")
    
    st.subheader("Diet Milestones")
    d1, d2 = st.columns(2)
    d1.metric("Days on Diet", len(df))
    # Est target date
    start_w = df.iloc[0]['Weight']
    latest_w = df.iloc[-1]['Weight']
    lbs_lost = start_w - latest_w
    weeks = (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7
    loss_per_week = lbs_lost / weeks if weeks > 0 else 0
    d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")

    with st.expander("See Raw Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("Waiting for data...")
